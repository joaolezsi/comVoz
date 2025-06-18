import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { SidebarComponent } from '../../sidebar/sidebar.component';
import { PlansService, TrocaPlano } from '../../services/plans.service';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-admin-planos',
  standalone: true,
  imports: [CommonModule, HttpClientModule, SidebarComponent],
  templateUrl: './admin-planos.component.html',
  styleUrls: ['./admin-planos.component.scss']
})
export class AdminPlanosComponent implements OnInit {
  trocas: TrocaPlano[] = [];
  carregando = true;

  constructor(
    private plansService: PlansService,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    console.log('Inicializando AdminPlanosComponent...');
    
    // Verificar se o usuário está logado
    if (!this.authService.isLoggedIn()) {
      console.error('Usuário não está logado');
      this.notificationService.error('Acesso Negado', 'Você precisa estar logado para acessar esta página.');
      return;
    }
    
    // Verificar se o usuário é admin
    if (!this.authService.isAdmin()) {
      console.error('Usuário não é admin');
      this.notificationService.error('Acesso Negado', 'Você não tem permissão para acessar esta página.');
      return;
    }
    
    // Verificar dados do usuário
    const currentUser = this.authService.getCurrentUser();
    console.log('Usuário atual:', currentUser);
    console.log('É admin?', this.authService.isAdmin());
    
    this.carregarSolicitacoes();
  }

  carregarSolicitacoes(): void {
    this.carregando = true;
    this.plansService.getAllInterests().subscribe({
      next: (data: TrocaPlano[]) => {
        this.trocas = data;
        this.carregando = false;
      },
      error: (error: any) => {
        console.error('Erro ao carregar solicitações:', error);
        this.notificationService.error('Erro ao Carregar', 'Erro ao carregar solicitações. Tente novamente mais tarde.');
        this.carregando = false;
      }
    });
  }

  responderSolicitacao(interestId: number, aprovado: boolean): void {
    const troca = this.trocas.find(t => t.id === interestId);
    if (!troca) {
      this.notificationService.error('Erro', 'Solicitação não encontrada');
      return;
    }

    this.carregando = true;

    const planId = troca.plan.id;
    const userId = troca.user.id;

    console.log('=== DADOS DA SOLICITAÇÃO ===');
    console.log('Interest ID:', interestId);
    console.log('Plan ID:', planId);
    console.log('User ID:', userId);
    console.log('Aprovado:', aprovado);
    console.log('Dados da troca:', troca);
    console.log('============================');

    if (!aprovado) {
      // Se for rejeição, apenas atualiza o status localmente
      troca.status = 'rejeitado';
      this.notificationService.success('Solicitação Rejeitada', 'Solicitação rejeitada com sucesso!');
      this.carregando = false;
      return;
    }

    // Se for aprovação, chama a API para ativar o plano
    this.plansService.responderSolicitacao(interestId, planId, userId).subscribe({
      next: (response: any) => {
        console.log('Resposta da API:', response);
        this.notificationService.success('Solicitação Aprovada', 'Solicitação aprovada com sucesso! O plano foi ativado para o usuário.');
        troca.status = 'aprovado';
        this.carregando = false;
      },
      error: (error: any) => {
        console.error('=== ERRO NA SOLICITAÇÃO ===');
        console.error('Status:', error.status);
        console.error('Erro completo:', error);
        console.error('Mensagem:', error.error);
        console.error('==========================');
        
        this.carregando = false;
        
        if (error.status === 422) {
          this.notificationService.error('Dados Inválidos', 'Dados inválidos para processar a solicitação. Verifique os dados e tente novamente.');
        } else if (error.status === 401 || error.status === 403) {
          this.notificationService.error('Acesso Negado', 'Você não tem permissão para realizar esta ação. Verifique se você está logado como administrador.');
        } else if (error.status === 400) {
          const errorMsg = error.error?.error || error.message || 'Erro de validação';
          this.notificationService.error('Erro de Validação', errorMsg);
        } else if (error.status === 404) {
          this.notificationService.error('Não Encontrado', 'Plano ou usuário não encontrado.');
        } else if (error.status === 500) {
          this.notificationService.error('Erro do Servidor', 'Erro interno do servidor. Tente novamente mais tarde.');
        } else {
          this.notificationService.error('Erro na Solicitação', 'Erro ao processar solicitação. Tente novamente mais tarde.');
        }
      }
    });
  }
} 