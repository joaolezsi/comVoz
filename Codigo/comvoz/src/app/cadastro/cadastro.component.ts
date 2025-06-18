import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { NotificationService } from '../services/notification.service';
import zxcvbn from 'zxcvbn';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, HttpClientModule],
  templateUrl: './cadastro.component.html',
  styleUrls: ['./cadastro.component.scss'],
})
export class CadastroComponent {
  cadastroForm: FormGroup;
  passwordStrength: number = 0; 
  passwordStrengthColor: string = ''; 
  isSubmitting: boolean = false;
  showPassword: boolean = false;
  showPasswordRepeat: boolean = false;

  constructor(
    private fb: FormBuilder, 
    private http: HttpClient, 
    private router: Router,
    private notificationService: NotificationService
  ) {
    this.cadastroForm = this.fb.group({
      nome: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      telefone: [''],
      empresa: [''],
      cargo: [''],
      cnpj: ['', [Validators.required, this.validateCnpj]],
      password: ['', [Validators.required, this.validatePasswordStrength]],
      passwordRepeat: ['', Validators.required],
    }, { validators: this.passwordMatchValidator });

    this.cadastroForm.get('password')?.valueChanges.subscribe((value) => {
      this.calculatePasswordStrength(value);
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  togglePasswordRepeatVisibility(): void {
    this.showPasswordRepeat = !this.showPasswordRepeat;
  }

  calculatePasswordStrength(password: string) {
    if (password) {
      const result = zxcvbn(password);
      this.passwordStrength = result.score; 
      this.updatePasswordStrengthColor();
    } else {
      this.passwordStrength = 0;
      this.passwordStrengthColor = '';
    }
  }

  
  updatePasswordStrengthColor() {
    switch (this.passwordStrength) {
      case 0:
      case 1:
        this.passwordStrengthColor = 'weak'; // Fraca (amarelo)

        break;
      case 2:
        this.passwordStrengthColor = 'good'; // Boa (verde claro)
        break;
      case 3:
      case 4:
        this.passwordStrengthColor = 'strong'; // Forte (verde escuro)
        break;
      default:
        this.passwordStrengthColor = '';
    }
  }

  validatePasswordStrength(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const result = zxcvbn(value);
    if (result.score < 2) { // Senha fraca (score < 2)
      return { passwordStrength: true };
    }
    return null;
  }

  validateCnpj(control: AbstractControl): ValidationErrors | null {
    const cnpj = control.value;
    if (!cnpj) return null;

    const cleanedCnpj = cnpj.replace(/\D/g, '');
    if (cleanedCnpj.length !== 14) return { invalidCnpj: true };

    // Algoritmo de validação do CNPJ (mesmo do código anterior)
    let size = cleanedCnpj.length - 2;
    let numbers = cleanedCnpj.substring(0, size);
    const digits = cleanedCnpj.substring(size);
    let sum = 0;
    let pos = size - 7;

    for (let i = size; i >= 1; i--) {
      sum += numbers.charAt(size - i) * pos--;
      if (pos < 2) pos = 9;
    }

    let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result !== parseInt(digits.charAt(0), 10)) return { invalidCnpj: true };

    size = size + 1;
    numbers = cleanedCnpj.substring(0, size);
    sum = 0;
    pos = size - 7;

    for (let i = size; i >= 1; i--) {
      sum += numbers.charAt(size - i) * pos--;
      if (pos < 2) pos = 9;
    }

    result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result !== parseInt(digits.charAt(1), 10)) return { invalidCnpj: true };

    return null;
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const passwordRepeat = control.get('passwordRepeat')?.value;

    if (password !== passwordRepeat) {
      return { passwordMismatch: true };
    }
    return null;
  }

  onSubmit() {
    if (this.cadastroForm.valid && !this.isSubmitting) {
      this.isSubmitting = true;
      
      // Endpoint da API de cadastro
      const apiUrl = 'http://127.0.0.1:8080/usuarios/resgistrar';
      
      // Preparando os dados do formulário para envio
      const formData = {
        nome_completo: this.cadastroForm.value.nome,
        email: this.cadastroForm.value.email,
        password: this.cadastroForm.value.password,
        passwordRepeat: this.cadastroForm.value.passwordRepeat,
        telefone: this.cadastroForm.value.telefone || '',
        empresa: this.cadastroForm.value.empresa || '',
        cargo: this.cadastroForm.value.cargo || '',
        cnpj: this.cadastroForm.value.cnpj
      };

      this.http.post(apiUrl, formData).subscribe({
        next: (response: any) => {
          console.log('Cadastro realizado com sucesso:', response);
          this.notificationService.success('Cadastro Realizado', 'Cadastro realizado com sucesso! Você será redirecionado para a página de login.');
          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 2000);
        },
        error: (error: HttpErrorResponse) => {
          this.isSubmitting = false;
          console.error('Erro ao cadastrar:', error);
          
          let errorMessage = '';
          
          if (error.status === 0) {
            errorMessage = 'Não foi possível conectar ao servidor. Verifique sua conexão de internet.';
          } else if (error.status === 400) {
            // Bad request - provavelmente dados inválidos
            errorMessage = error.error?.message || 'Dados inválidos. Verifique as informações fornecidas.';
          } else if (error.status === 409) {
            // Conflito - usuário já existe
            errorMessage = 'Este email já está registrado. Por favor, use outro email ou faça login.';
          } else {
            errorMessage = 'Ocorreu um erro ao processar seu cadastro. Por favor, tente novamente mais tarde.';
          }
          
          this.notificationService.error('Erro no Cadastro', errorMessage);
        },
        complete: () => {
          this.isSubmitting = false;
        }
      });
    }
  }
}