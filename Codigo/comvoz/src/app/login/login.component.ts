import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, HttpClientModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  loginForm: FormGroup;
  loginError: boolean = false;
  isSubmitting: boolean = false;
  errorMessage: string = '';
  showPassword: boolean = false;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private notificationService: NotificationService
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  onSubmit() {
    if (this.loginForm.valid && !this.isSubmitting) {
      this.isSubmitting = true;
      this.loginError = false;
      this.errorMessage = '';
      
      const email = this.loginForm.value.email;
      const password = this.loginForm.value.password;

      this.authService.login(email, password).subscribe({
        next: () => {
          // Mostrar notificação de sucesso
          this.notificationService.showLoginSucesso();
          // Redirecionar para o dashboard após login bem sucedido
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.isSubmitting = false;
          
          if (error.status === 0) {
            this.notificationService.showErroConexao();
          } else if (error.status === 401) {
            this.notificationService.error('Login Inválido', 'Email ou senha incorretos. Por favor, tente novamente.');
          } else if (error.status === 403) {
            this.notificationService.error('Acesso Negado', 'Sua conta pode estar desativada. Entre em contato com o suporte.');
          } else {
            this.notificationService.error('Erro no Login', 'Erro ao fazer login. Por favor, tente novamente mais tarde.');
          }
          
          this.loginError = true;
        },
        complete: () => {
          this.isSubmitting = false;
        }
      });
    }
  }
}