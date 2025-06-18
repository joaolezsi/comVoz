import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { Router } from '@angular/router';
import { PlanoService } from '../services/plano.service';
import { Plano as PlanoAPI } from '../services/plano.service';
import { NotificationService } from '../services/notification.service';

interface PlanoLimite {
  descricao: string;
  valor: string | number;
}

interface Plano {
  id: number;
  nome: string;
  preco: string;
  itens: PlanoLimite[];
}

@Component({
  selector: 'app-planos',
  standalone: true,
  imports: [CommonModule, HttpClientModule, SidebarComponent],
  templateUrl: './planos.component.html',
  styleUrls: ['./planos.component.scss']
})
export class PlanosComponent implements OnInit {
  planos: Plano[] = [];
  carregando: boolean = true;
  erroCarregamento: string = '';
  planoAtualId: number | null = null;
  planoInteresseId: number | null = null;
  enviandoInteresse: boolean = false;

  constructor(
    private planoService: PlanoService,
    private router: Router,
    private notificationService: NotificationService
  ) {
    // Recupera o plano de interesse do localStorage ao inicializar
    const planoInteresse = localStorage.getItem('planoInteresse');
    if (planoInteresse) {
      this.planoInteresseId = parseInt(planoInteresse, 10);
    }
  }

  ngOnInit(): void {
    this.carregarPlanos();
    this.carregarPlanoAtual();
    this.carregarPlanoInteresse();
  }

  carregarPlanos(): void {
    this.carregando = true;
    this.erroCarregamento = '';

    this.planoService.getPlanos()
      .subscribe({
        next: (data) => {
          this.planos = data.map(plano => {
            let itens: PlanoLimite[] = [];

            if (plano.id === 1) {
              itens = [
                { descricao: 'Quantidade de questões', valor: '5' },
                { descricao: 'Amostra', valor: '100' },
                { descricao: 'Disparo', valor: '✓' },
                { descricao: 'QR Code', valor: '✗' },
                { descricao: 'Relatório Online', valor: '✗' },
                { descricao: 'Resultados em Reunião', valor: '✗' },
                { descricao: 'Comparação com Concorrência', valor: '✗' }
              ];
            } else if (plano.id === 2) {
              itens = [
                { descricao: 'Quantidade de questões', valor: '6' },
                { descricao: 'Amostra', valor: '200' },
                { descricao: 'Disparo', valor: '✓' },
                { descricao: 'QR Code', valor: '✓' },
                { descricao: 'Relatório Online', valor: '✓' },
                { descricao: 'Resultados em Reunião', valor: '✗' },
                { descricao: 'Comparação com Concorrência', valor: '✗' }
              ];
            } else if (plano.id === 3) {
              itens = [
                { descricao: 'Quantidade de questões', valor: '8' },
                { descricao: 'Amostra', valor: '500' },
                { descricao: 'Disparo', valor: '✓' },
                { descricao: 'QR Code', valor: '✓' },
                { descricao: 'Relatório Online', valor: '✓' },
                { descricao: 'Resultados em Reunião', valor: '✓' },
                { descricao: 'Comparação com Concorrência', valor: '✗' }
              ];
            } else if (plano.id === 4) {
              itens = [
                { descricao: 'Quantidade de questões', valor: 'Ilimitado' },
                { descricao: 'Amostra', valor: 'Ilimitado' },
                { descricao: 'Disparo', valor: '✓' },
                { descricao: 'QR Code', valor: '✓' },
                { descricao: 'Relatório Online', valor: '✓' },
                { descricao: 'Resultados em Reunião', valor: '✓' },
                { descricao: 'Comparação com Concorrência', valor: '✓' }
              ];
            }

            return {
              id: plano.id,
              nome: plano.nome,
              preco: `R$ ${plano.preco.toFixed(2).replace('.', ',')}`,
              itens: itens
            };
          });
          this.carregando = false;
        },
        error: (error) => {
          console.error('Erro ao carregar planos:', error);
          
          if (error.status === 401 || error.status === 403) {
            this.notificationService.error('Sessão Expirada', 'Por favor, faça login novamente para continuar.');
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
          } else {
            this.notificationService.showErroConexao();
          }
          
          this.carregando = false;
        }
      });
  }

  carregarPlanoAtual(): void {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        
        if (user && user.id) {
          this.planoService.getPlanoUsuario(user.id)
            .subscribe({
              next: (plano) => {
                if (plano) {
                  this.planoAtualId = plano.id;
                }
              },
              error: (error) => {
                console.error('Erro ao carregar plano do usuário:', error);
              }
            });
        }
        
      } catch (error) {
        console.error('Erro ao processar dados do usuário:', error);
      }
    }
  }

  carregarPlanoInteresse(): void {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        if (user && user.id) {
          this.planoService.getPlanosInteresse(user.id)
            .subscribe({
              next: (planos) => {
                if (planos && planos.length > 0) {
                  this.planoInteresseId = planos[0].id;
                  localStorage.setItem('planoInteresse', this.planoInteresseId.toString());
                } else {
                  // Se não houver planos de interesse, limpa o estado
                  this.planoInteresseId = null;
                  localStorage.removeItem('planoInteresse');
                }
              },
              error: (error) => {
                console.error('Erro ao carregar plano de interesse:', error);
                // Em caso de erro, limpa o estado
                this.planoInteresseId = null;
                localStorage.removeItem('planoInteresse');
              }
            });
        } else {
          // Se não houver usuário, limpa o estado
          this.planoInteresseId = null;
          localStorage.removeItem('planoInteresse');
        }
      } catch (error) {
        console.error('Erro ao processar dados do usuário:', error);
        // Em caso de erro, limpa o estado
        this.planoInteresseId = null;
        localStorage.removeItem('planoInteresse');
      }
    } else {
      // Se não houver dados do usuário, limpa o estado
      this.planoInteresseId = null;
      localStorage.removeItem('planoInteresse');
    }
  }

  isPlanoAtual(planoId: number): boolean {
    return this.planoAtualId === planoId;
  }

  isInteresseRegistrado(planoId: number): boolean {
    return this.planoInteresseId === planoId;
  }

  isBotaoDesabilitado(planoId: number): boolean {
    return this.isPlanoAtual(planoId) || 
           this.isInteresseRegistrado(planoId) || 
           (this.planoInteresseId !== null && !this.isInteresseRegistrado(planoId));
  }

  selecionarPlano(planoId: number): void {
    if (this.planoAtualId === planoId || this.isInteresseRegistrado(planoId)) return;

    const userData = localStorage.getItem('user');
    if (!userData) {
      this.notificationService.warning('Login Necessário', 'Você precisa estar logado para selecionar um plano.');
      this.router.navigate(['/login']);
      return;
    }

    try {
      const user = JSON.parse(userData);
      
      if (planoId === 1) {
        this.notificationService.info('Plano Gratuito', 'O plano gratuito já está disponível para todos os usuários.');
        return;
      }
      this.enviandoInteresse = true;
      this.planoService.registrarInteresse(planoId, user.id)
        .subscribe({
          next: (response) => {
            this.enviandoInteresse = false;
            this.planoInteresseId = planoId;
            localStorage.setItem('planoInteresse', planoId.toString());
            this.notificationService.success(
              'Interesse Registrado', 
              'Nossa equipe entrará em contato em breve para finalizar a contratação do plano.',
              0,
              [
                {
                  label: 'Ver Contatos',
                  action: () => this.router.navigate(['/contatos']),
                  style: 'primary'
                }
              ]
            );
          },
          error: (error) => {
            this.enviandoInteresse = false;
            console.error('Erro ao registrar interesse:', error);
            
            if (error.status === 401 || error.status === 403) {
              this.notificationService.error('Sessão Expirada', 'Por favor, faça login novamente.');
              this.router.navigate(['/login']);
            } else if (error.status === 409) {
              this.notificationService.warning('Interesse Já Registrado', 'Você já possui um interesse registrado. Aguarde o contato da nossa equipe.');
              this.planoInteresseId = planoId;
              localStorage.setItem('planoInteresse', planoId.toString());
            } else if (error.status === 400) {
              this.notificationService.info('Plano Ativo', 'Você já possui um plano ativo. Entre em contato conosco para mais informações.');
            } else {
              this.notificationService.error('Erro no Registro', 'Não foi possível registrar o interesse. Tente novamente mais tarde.');
            }
          }
        });
        
    } catch (error) {
      this.enviandoInteresse = false;
      console.error('Erro ao processar dados do usuário:', error);
      this.notificationService.error('Erro de Dados', 'Erro ao processar dados do usuário. Por favor, faça login novamente.');
      this.router.navigate(['/login']);
    }
  }
}