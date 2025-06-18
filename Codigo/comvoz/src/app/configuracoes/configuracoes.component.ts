import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { UserService, UserProfile, UpdateProfileData } from '../services/user.service';
import { NotificationService } from '../services/notification.service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-configuracoes',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, SidebarComponent],
  templateUrl: './configuracoes.component.html',
  styleUrls: ['./configuracoes.component.scss']
})
export class ConfiguracoesComponent implements OnInit {
  profileForm: FormGroup;
  userProfile: UserProfile | null = null;
  carregando = false;
  salvando = false;

  constructor(
    private fb: FormBuilder,
    private userService: UserService,
    private notificationService: NotificationService,
    private authService: AuthService,
    private router: Router
  ) {
    this.profileForm = this.fb.group({
      nome_completo: ['', [Validators.required, Validators.minLength(2)]],
      telefone: ['', [Validators.required]],
      empresa: ['', [Validators.required]],
      cargo: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.carregarPerfilUsuario();
  }

  carregarPerfilUsuario(): void {
    this.carregando = true;
    
    this.userService.getUserProfile().subscribe({
      next: (profile) => {
        this.userProfile = profile;
        this.preencherFormulario(profile);
        this.carregando = false;
      },
      error: (error) => {
        console.error('Erro ao carregar perfil:', error);
        this.carregando = false;
        
        if (error.status === 401) {
          this.notificationService.error('Sessão Expirada', 'Sua sessão expirou. Faça login novamente.');
          this.authService.logout();
          this.router.navigate(['/login']);
        } else {
          this.notificationService.error('Erro ao Carregar', 'Não foi possível carregar suas informações. Tente novamente.');
        }
      }
    });
  }

  preencherFormulario(profile: UserProfile): void {
    this.profileForm.patchValue({
      nome_completo: profile.nome_completo,
      telefone: profile.telefone,
      empresa: profile.empresa,
      cargo: profile.cargo
    });
  }

  onSubmit(): void {
    if (this.profileForm.invalid) {
      this.notificationService.warning('Formulário Inválido', 'Por favor, preencha todos os campos obrigatórios.');
      this.markFormGroupTouched();
      return;
    }

    const formData = this.profileForm.value;
    
    // Verifica se houve alguma alteração
    if (this.userProfile && this.dadosNaoForamAlterados(formData)) {
      this.notificationService.info('Nenhuma Alteração', 'Nenhuma alteração foi detectada.');
      return;
    }

    this.salvarAlteracoes(formData);
  }

  private dadosNaoForamAlterados(formData: UpdateProfileData): boolean {
    if (!this.userProfile) return false;
    
    return (
      formData.nome_completo === this.userProfile.nome_completo &&
      formData.telefone === this.userProfile.telefone &&
      formData.empresa === this.userProfile.empresa &&
      formData.cargo === this.userProfile.cargo
    );
  }

  salvarAlteracoes(profileData: UpdateProfileData): void {
    this.salvando = true;

    this.userService.updateUserProfile(profileData).subscribe({
      next: (response) => {
        this.salvando = false;
        this.notificationService.success('Perfil Atualizado', 'Suas informações foram atualizadas com sucesso!');
        
        // Atualiza os dados do usuário no localStorage
        if (response.user) {
          this.userProfile = response.user;
          this.authService.updateUserData(response.user);
        }
      },
      error: (error) => {
        console.error('Erro ao atualizar perfil:', error);
        this.salvando = false;
        
        if (error.status === 401) {
          this.notificationService.error('Sessão Expirada', 'Sua sessão expirou. Faça login novamente.');
          this.authService.logout();
          this.router.navigate(['/login']);
        } else if (error.status === 400) {
          this.notificationService.error('Dados Inválidos', error.error?.error || 'Dados fornecidos são inválidos.');
        } else {
          this.notificationService.error('Erro ao Salvar', 'Não foi possível salvar as alterações. Tente novamente.');
        }
      }
    });
  }

  cancelarEdicao(): void {
    if (this.userProfile) {
      this.preencherFormulario(this.userProfile);
      this.notificationService.info('Alterações Canceladas', 'As alterações foram descartadas.');
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.profileForm.controls).forEach(key => {
      const control = this.profileForm.get(key);
      if (control) {
        control.markAsTouched();
      }
    });
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.profileForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  getFieldError(fieldName: string): string {
    const field = this.profileForm.get(fieldName);
    if (field && field.errors && (field.dirty || field.touched)) {
      if (field.errors['required']) {
        return 'Este campo é obrigatório';
      }
      if (field.errors['minlength']) {
        return `Mínimo de ${field.errors['minlength'].requiredLength} caracteres`;
      }
    }
    return '';
  }
} 