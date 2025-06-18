import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { AuthService } from '../services/auth.service';
import { PlanoService, Plano } from '../services/plano.service';
import { NotificationService } from '../services/notification.service';

interface Pesquisa {
  _id: string;
  titulo: string;
  descricao: string;
  ativo: boolean;
  data_criacao: string;
  user_id: number;
  cnpj: string;
  perguntas: any[];
}

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  subItems?: MenuItem[];
}

@Component({
  selector: 'app-pesquisas',
  templateUrl: './pesquisas.component.html',
  styleUrls: ['./pesquisas.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, RouterModule, SidebarComponent]
})
export class PesquisasComponent implements OnInit {
  pesquisas: Pesquisa[] = [];
  pesquisasFiltradas: Pesquisa[] = [];
  filtroAtivo: boolean | null = null;
  termoBusca: string = '';
  plano: Plano | null = null;
  pesquisasRestantes: number = 0;
  carregandoPlano: boolean = true;
  enviandoPesquisa: boolean = false;

  constructor(
    private http: HttpClient,
    private router: Router,
    private authService: AuthService,
    private planoService: PlanoService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.carregarPesquisas();
    this.carregarPlanoUsuario();
  }

  carregarPlanoUsuario(): void {
    const currentUser = this.authService.getCurrentUser();
    console.log('Usuário atual:', currentUser);
    
    this.carregandoPlano = true;
    
    if (currentUser && currentUser.id) {
      console.log('Carregando plano do usuário ID:', currentUser.id);
      
      this.planoService.getPlanoUsuario(currentUser.id).subscribe({
        next: (plano) => {
          console.log('Plano carregado com sucesso:', plano);
          this.plano = plano;
          this.carregandoPlano = false;
          this.calcularPesquisasRestantes();
        },
        error: (error) => {
          console.error('Erro ao carregar plano do usuário:', error);
          console.error('Status:', error.status);
          console.error('Mensagem:', error.message);
          
          if (error.status === 404) {
            // Usuário não possui plano ativo - mostrar plano gratuito padrão
            this.plano = {
              id: 1,
              nome: 'Plano Gratuito',
              preco: 0,
              limite_pesquisas: 5,
              descricao: 'Plano gratuito padrão'
            };
            console.log('Usuário sem plano ativo - usando plano gratuito padrão');
          } else if (error.status === 401 || error.status === 403) {
            // Erro de autenticação - redirecionar para login
            this.notificationService.error('Sessão Expirada', 'Por favor, faça login novamente.');
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
            return;
          } else {
            // Outros erros - usar fallback
            this.plano = {
              id: 0,
              nome: 'Plano Básico',
              preco: 0,
              limite_pesquisas: 5,
              descricao: 'Plano básico padrão'
            };
            console.log('Erro desconhecido - usando fallback');
          }
          
          this.carregandoPlano = false;
          this.calcularPesquisasRestantes();
        }
      });
    } else {
      console.warn('Usuário não encontrado ou sem ID');
      // Fallback: usar um plano gratuito padrão
      this.plano = {
        id: 1,
        nome: 'Plano Gratuito',
        preco: 0,
        limite_pesquisas: 5,
        descricao: 'Plano gratuito padrão'
      };
      this.carregandoPlano = false;
      this.calcularPesquisasRestantes();
    }
  }

  calcularPesquisasRestantes(): void {
    if (this.plano && this.plano.limite_pesquisas !== undefined) {
      const totalPesquisas = this.pesquisas ? this.pesquisas.length : 0;
      this.pesquisasRestantes = Math.max(0, this.plano.limite_pesquisas - totalPesquisas);
      console.log(`Pesquisas restantes: ${this.pesquisasRestantes} (Limite: ${this.plano.limite_pesquisas}, Criadas: ${totalPesquisas})`);
    } else {
      this.pesquisasRestantes = 0;
      console.warn('Plano não definido ou sem limite de pesquisas');
    }
  }

  carregarPesquisas(): void {
    let url = 'http://127.0.0.1:8080/pesquisas';
    if (this.filtroAtivo !== null) {
      url += `?ativa=${this.filtroAtivo}`;
    }

    try {
      const headers = this.authService.getAuthHeaders();
      
      this.http.get<Pesquisa[]>(url, { headers }).subscribe({
        next: (data) => {
          this.pesquisas = data;
          this.aplicarFiltros();
          this.calcularPesquisasRestantes();
        },
        error: (error) => {
          console.error('Erro ao carregar pesquisas:', error);
          this.notificationService.error('Erro ao Carregar', 'Erro ao carregar pesquisas. Tente novamente mais tarde.');
        }
      });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      this.notificationService.error('Erro de Autenticação', 'Por favor, faça login novamente.');
      this.router.navigate(['/login']);
    }
  }

  aplicarFiltros(): void {
    this.pesquisasFiltradas = this.pesquisas.filter(pesquisa => {
      const matchBusca = !this.termoBusca || 
        pesquisa.titulo.toLowerCase().includes(this.termoBusca.toLowerCase()) ||
        pesquisa.descricao.toLowerCase().includes(this.termoBusca.toLowerCase());

      const matchStatus = this.filtroAtivo === null || pesquisa.ativo === this.filtroAtivo;

      return matchBusca && matchStatus;
    });
  }

  onBuscaChange(): void {
    this.aplicarFiltros();
  }

  filtrarPesquisas(ativo: boolean | null): void {
    this.filtroAtivo = ativo;
    this.aplicarFiltros();
  }

  onSidebarItemSelected(item: MenuItem): void {
    if (item.route) {
      this.router.navigate([item.route]);
    }
  }

  formatarData(data: string): string {
    return new Date(data).toLocaleDateString('pt-BR');
  }

  alternarStatusPesquisa(pesquisa: Pesquisa): void {
    const novoStatus = !pesquisa.ativo;
    const endpoint = novoStatus ? 'ativar' : 'desativar';
    
    try {
      const headers = this.authService.getAuthHeaders();
      
      this.http.patch(`http://127.0.0.1:8080/pesquisas/${pesquisa._id}/${endpoint}`, {}, { headers }).subscribe({
        next: () => {
          pesquisa.ativo = novoStatus;
          this.notificationService.success(
            'Status Alterado', 
            `Pesquisa ${novoStatus ? 'ativada' : 'desativada'} com sucesso!`
          );
        },
        error: (error) => {
          console.error('Erro ao alterar status da pesquisa:', error);
          this.notificationService.error('Erro ao Alterar', 'Erro ao alterar status da pesquisa. Tente novamente mais tarde.');
        }
      });
    } catch (error) {
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      this.notificationService.error('Erro de Autenticação', 'Por favor, faça login novamente.');
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
    }
  }

  verRelatorio(pesquisaId: string): void {
    this.router.navigate(['/relatorios', pesquisaId]);
  }

  criarNovaPesquisa(): void {
    if (this.pesquisasRestantes <= 0) {
      this.notificationService.warning('Limite Atingido', 'Você atingiu o limite de pesquisas do seu plano. Considere fazer upgrade.');
      return;
    }
    this.notificationService.info('Redirecionando', 'Redirecionando para seleção de questões...');
    this.router.navigate(['/questoes']);
  }

  enviarPesquisa(pesquisaId: string): void {
    try {
      const headers = this.authService.getAuthHeaders();
      this.enviandoPesquisa = true;
      console.log('=== DADOS DO ENVIO DE PESQUISA ===');
      console.log('URL:', `http://127.0.0.1:8080/pesquisas/enviar_pesquisa/${pesquisaId}`);
      console.log('Headers:', headers);
      console.log('Body:', {});
      console.log('================================');

      this.http.post(`http://127.0.0.1:8080/pesquisas/enviar_pesquisa/${pesquisaId}`, {}, { headers }).subscribe({
        next: (response: any) => {
          this.enviandoPesquisa = false;
          this.notificationService.success('Pesquisa Enviada', response.message || 'Pesquisa enviada com sucesso!');
        },
        error: (error) => {
          this.enviandoPesquisa = false;
          console.error('Erro ao enviar pesquisa:', error);
          this.notificationService.error('Erro no Envio', error.error?.error || 'Erro ao enviar pesquisa. Tente novamente mais tarde.');
        }
      });
    } catch (error) {
      this.enviandoPesquisa = false;
      console.error('Erro ao obter cabeçalhos de autenticação:', error);
      this.notificationService.error('Erro de Autenticação', 'Por favor, faça login novamente.');
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
    }
  }

  gerarLinkPesquisa(pesquisaId: string): void {
    const link = `http://localhost:4200/responder?id=${pesquisaId}`;
    console.log('Link da Pesquisa:', link);
    this.notificationService.info('Link da Pesquisa', link);
  }
} 