import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { RelatorioService } from '../services/relatorio.service';
import { NotificationService } from '../services/notification.service';

interface UserProfile {
  id: number;
  nome_completo: string;
  email: string;
  plano?: {
    id: number;
    nome: string;
    limites: {
      pesquisas: number;
      envios: number;
    }
  }
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule, SidebarComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  userProfile: UserProfile | null = null;
  pesquisasAtivas: number = 0;
  respostasRecebidas: number = 0;
  taxaResposta: number = 0;
  scoreNPS: number = 0;
  carregando: boolean = true;

  constructor(
    private http: HttpClient,
    private router: Router,
    private relatorioService: RelatorioService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.carregarDadosUsuario();
    this.carregarEstatisticas();
  }

  carregarDadosUsuario(): void {
    const userData = localStorage.getItem('user');
    
    if (userData) {
      try {
        const user = JSON.parse(userData);
        const token = localStorage.getItem('token');
        
        if (!token) {
          console.error('Token não encontrado');
          this.userProfile = user;
          return;
        }
        
        const headers = new HttpHeaders({
          'Authorization': `Basic ${token}`
        });
        
        // Carregar dados completos do usuário do backend
        this.http.get<UserProfile>(`http://127.0.0.1:8080/usuarios/${user.id}`, { headers }).subscribe({
          next: (profile) => {
            this.userProfile = profile;
          },
          error: (error) => {
            console.error('Erro ao carregar perfil:', error);
            // Use os dados básicos do localStorage como fallback
            this.userProfile = user;
          }
        });
      } catch (e) {
        console.error('Erro ao processar dados do usuário:', e);
      }
    } else {
      // Redirecionar para login se não houver dados de usuário
      this.router.navigate(['/login']);
    }
  }

  carregarEstatisticas(): void {
    this.carregando = true;

    this.relatorioService.getEstatisticasResumo()
      .subscribe({
        next: (data) => {
          this.pesquisasAtivas = data.pesquisas_ativas || 0;
          this.respostasRecebidas = data.respostas_recebidas || 0;
          this.taxaResposta = data.taxa_resposta || 0;
          this.scoreNPS = this.formatarScoreNPS(data.score);
          this.carregando = false;
        },
        error: (error) => {
          console.error('Erro ao carregar estatísticas:', error);
          this.notificationService.error('Erro ao Carregar', 'Não foi possível carregar as estatísticas. Tente novamente mais tarde.');
          this.carregando = false;
        }
      });
  }

  private formatarScoreNPS(score: any): number {
    // Se o score for null, undefined, string, ou qualquer valor inválido, retorna 0
    if (score === null || score === undefined || typeof score === 'string' || isNaN(score)) {
      return 0;
    }
    
    // Se for um número válido, retorna ele
    return Math.round(score);
  }

  navegarPara(rota: string): void {
    this.router.navigate([rota]);
  }
} 