// questoes.component.ts

import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

// Interfaces
interface Alternativa {
  id: number;
  texto: string;
}

interface Questao {
  id: number;
  texto: string;
  tipo: string;
  opcoes: Alternativa[] | null;
  user_id: number | null;
  selecionada?: boolean;
}

interface NovaQuestaoForm {
  texto: string;
  tipoResposta: string;
  alternativas: Alternativa[];
  maxCaracteres?: number;
}

interface QuestaoDTO {
  user_id: number;
  questoes: Array<{
    texto: string;
    tipo: number;
    opcoes: Array<{
      texto: string;
    }>;
  }>;
}

interface PesquisaDTO {
  user_id: number;
  titulo: string;
  perguntas: number[];
  descricao: string;
}

interface UserProfile {
  id: number;
  nome: string;
  email: string;
  cnpj: string;
}

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  subItems?: MenuItem[];
}

@Component({
  selector: 'app-questoes',
  templateUrl: './questoes.component.html',
  styleUrls: ['./questoes.component.scss'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule, FormsModule, HttpClientModule, SidebarComponent],
})
export class QuestoesComponent implements OnInit {
  // Tipos de resposta disponíveis
  tiposResposta = [
    { id: 'escolha', nome: 'Múltipla Escolha', icone: 'check_box' },
    { id: 'nps', nome: 'NPS (1-10)', icone: 'sentiment_satisfied' },
    { id: 'texto', nome: 'Texto Livre', icone: 'short_text' }
  ];

  // Dados
  questoes: Questao[] = [];
  questoesFiltradas: Questao[] = [];
  modalAberto: boolean = false;
  novaQuestao: NovaQuestaoForm = this.resetNovaQuestao();
  novaAlternativa: string = '';
  carregando: boolean = false;
  userProfile: UserProfile | null = null;
  novaPesquisaModalAberto: boolean = false;
  novaPesquisaTitulo: string = '';
  novaPesquisaDescricao: string = '';
  termoBusca: string = '';
  filtroTipo: string | null = null;

  constructor(
    private http: HttpClient,
    private router: Router,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.carregarDadosUsuario();
    this.carregarQuestoes();
  }

  carregarDadosUsuario(): void {
    const userData = localStorage.getItem('user');
    
    if (userData) {
      try {
        this.userProfile = JSON.parse(userData);
      } catch (e) {
        console.error('Erro ao processar dados do usuário:', e);
        this.notificationService.error('Erro de Dados', 'Erro ao carregar dados do usuário');
      }
    } else {
      console.warn('Usuário não encontrado no localStorage');
      this.router.navigate(['/login']);
    }
  }

  carregarQuestoes(): void {
    this.carregando = true;
    
    try {
      const headers = this.authService.getAuthHeaders();
      const userId = this.userProfile?.id || 1;
      
      this.http.get<Questao[]>(`http://127.0.0.1:8080/get_questoes/${userId}`, { headers }).subscribe({
        next: (data) => {
          this.questoes = data;
          this.aplicarFiltros();
          this.carregando = false;
        },
        error: (error) => {
          console.error('Erro ao carregar questões:', error);
          this.notificationService.warning('Carregando Exemplos', 'Erro ao carregar questões. Carregando exemplos...');
          
          this.carregarQuestoesExemplo();
          this.aplicarFiltros();
          this.carregando = false;
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

  carregarQuestoesExemplo(): void {
    this.questoes = [
      { 
        id: 1,
        texto: 'Qual seu nível de satisfação com nossos serviços?',
        tipo: 'emoji',
        opcoes: null,
        user_id: null,
        selecionada: false
      },
      { 
        id: 2,
        texto: 'Você recomendaria nossos serviços para um amigo?',
        tipo: 'radio',
        opcoes: [
          { id: 1, texto: 'Certamente não' },
          { id: 2, texto: 'Provavelmente não' },
          { id: 3, texto: 'Talvez' },
          { id: 4, texto: 'Provavelmente sim' },
          { id: 5, texto: 'Certamente sim' }
        ],
        user_id: null,
        selecionada: false
      },
      { 
        id: 3,
        texto: 'Quais aspectos você mais gostou em nossos serviços?',
        tipo: 'checkbox',
        opcoes: [
          { id: 1, texto: 'Atendimento' },
          { id: 2, texto: 'Qualidade' },
          { id: 3, texto: 'Preço' },
          { id: 4, texto: 'Prazo de entrega' }
        ],
        user_id: null,
        selecionada: false
      }
    ];
  }

  aplicarFiltros(): void {
    this.questoesFiltradas = this.questoes.filter(questao => {
      const matchBusca = !this.termoBusca || 
        questao.texto.toLowerCase().includes(this.termoBusca.toLowerCase()) ||
        (questao.opcoes && questao.opcoes.some(opcao => 
          opcao.texto.toLowerCase().includes(this.termoBusca.toLowerCase())
        ));

      const matchTipo = !this.filtroTipo || questao.tipo === this.filtroTipo;

      return matchBusca && matchTipo;
    });
  }

  onBuscaChange(): void {
    this.aplicarFiltros();
  }

  onFiltroTipoChange(tipo: string | null): void {
    this.filtroTipo = tipo;
    this.aplicarFiltros();
  }

  // Retorna as questões selecionadas para o template
  getQuestoesSelecionadas(): Questao[] {
    return this.questoes.filter(q => q.selecionada);
  }

  // Retorna a contagem de questões selecionadas
  getQuestoesSelecionadasCount(): number {
    return this.getQuestoesSelecionadas().length;
  }

  abrirModalNovaPesquisa(): void {
    if (!this.temSelecao) {
      this.notificationService.warning('Seleção Necessária', 'Selecione pelo menos uma questão');
      return;
    }

    this.novaPesquisaModalAberto = true;
  }

  fecharModalNovaPesquisa(): void {
    this.novaPesquisaModalAberto = false;
  }

  processarQuestoesSelecionadas(): void {
    if (!this.novaPesquisaTitulo.trim() || !this.novaPesquisaDescricao.trim()) {
      this.notificationService.warning('Campos Obrigatórios', 'Por favor, preencha o título e a descrição da pesquisa.');
      return;
    }

    const questoesSelecionadas = this.getQuestoesSelecionadas();
    if (questoesSelecionadas.length === 0) {
      this.notificationService.warning('Seleção Necessária', 'Por favor, selecione pelo menos uma questão para a pesquisa.');
      return;
    }

    // Verificar se existe userProfile
    if (!this.userProfile || !this.userProfile.id) {
      this.notificationService.error('Erro de Usuário', 'Usuário não identificado. Por favor, faça login novamente.');
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
      return;
    }

    // Criar a pesquisa
    const pesquisaData: PesquisaDTO = {
      user_id: this.userProfile.id,
      titulo: this.novaPesquisaTitulo.trim(),
      descricao: this.novaPesquisaDescricao.trim(),
      perguntas: questoesSelecionadas.map(q => q.id)
    };

    try {
      const headers = this.authService.getAuthHeaders();

      this.http.post('http://127.0.0.1:8080/criar_pesquisa', pesquisaData, { headers }).subscribe({
        next: (response: any) => {
          console.log('Pesquisa criada com sucesso:', response);
          this.notificationService.showPesquisaCriada();
          
          // Limpar seleções e fechar modal
          this.questoes.forEach(q => q.selecionada = false);
          this.novaPesquisaTitulo = '';
          this.novaPesquisaDescricao = '';
          this.fecharModalNovaPesquisa();
          
          // Redirecionar para a lista de pesquisas
          setTimeout(() => {
            this.router.navigate(['/pesquisas']);
          }, 1500);
        },
        error: (error) => {
          console.error('Erro ao criar pesquisa:', error);
          
          if (error.status === 403) {
            this.notificationService.error('Limite Atingido', 'Você atingiu o limite de pesquisas para seu plano atual.');
          } else if (error.status === 400) {
            const errorMessage = error.error?.message || error.error?.error || 'Dados inválidos. Verifique se todos os campos estão preenchidos corretamente.';
            this.notificationService.error('Dados Inválidos', errorMessage);
          } else {
            this.notificationService.error('Erro ao Criar', 'Erro ao criar pesquisa. Por favor, tente novamente mais tarde.');
          }
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

  // Reseta o formulário de nova questão
  private resetNovaQuestao(): NovaQuestaoForm {
    return {
      texto: '',
      tipoResposta: 'checkbox',
      alternativas: [],
      maxCaracteres: 500
    };
  }

  // Verifica se alguma questão está selecionada
  get temSelecao(): boolean {
    return this.questoes.some((questao) => questao.selecionada);
  }

  // Alterna a seleção de uma questão
  alternarSelecao(questao: Questao): void {
    questao.selecionada = !questao.selecionada;
  }

  // Abre o modal para adicionar questão
  abrirModal(): void {
    this.modalAberto = true;
    this.novaQuestao = this.resetNovaQuestao();
    this.novaAlternativa = '';
  }

  // Fecha o modal
  fecharModal(): void {
    this.modalAberto = false;
  }

  // Adiciona uma nova questão
  adicionarQuestao(): void {
    if (!this.questaoValida()) {
      return;
    }

    if (!this.userProfile || !this.userProfile.id) {
      this.notificationService.error('Erro de Usuário', 'Usuário não identificado. Por favor, faça login novamente.');
      return;
    }

    const questaoData: QuestaoDTO = {
      user_id: this.userProfile.id,
      questoes: [{
        texto: this.novaQuestao.texto,
        tipo: this.mapTipoRespostaParaNumero(this.novaQuestao.tipoResposta),
        opcoes: this.novaQuestao.alternativas.map(alt => ({ texto: alt.texto }))
      }]
    };

    try {
      const headers = this.authService.getAuthHeaders();

      this.http.post('http://127.0.0.1:8080/criar_questoes', questaoData, { headers }).subscribe({
        next: (response: any) => {
          console.log('Questão adicionada:', response);
          this.notificationService.showQuestaoAdicionada();
          
          // Limpar formulário e fechar modal
          this.novaQuestao = this.resetNovaQuestao();
          this.fecharModal();
          
          // Recarregar questões
          this.carregarQuestoes();
        },
        error: (error) => {
          console.error('Erro ao adicionar questão:', error);
          this.notificationService.error('Erro ao Adicionar', 'Erro ao adicionar questão. Por favor, tente novamente.');
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

  private mapTipoRespostaParaNumero(tipo: string): number {
    const tiposMap: { [key: string]: number } = {
      'escolha': 1,
      'nps': 2,
      'texto': 3
    };
    return tiposMap[tipo] || 1;
  }

  adicionarAlternativa(): void {
    if (!this.novaAlternativa.trim()) return;
    
    this.novaQuestao.alternativas.push({
      id: this.novaQuestao.alternativas.length + 1,
      texto: this.novaAlternativa.trim()
    });
    this.novaAlternativa = '';
  }

  removerAlternativa(index: number): void {
    this.novaQuestao.alternativas.splice(index, 1);
  }

  questaoValida(): boolean {
    const questao = this.novaQuestao;
    
    if (!questao.texto?.trim() || !questao.tipoResposta) {
      return false;
    }

    switch (questao.tipoResposta) {
      case 'checkbox':
        return questao.alternativas.length >= 2;
      case 'nps':
        return true; // NPS não precisa de validação adicional
      case 'texto':
        return true; // Texto não precisa de validação adicional
      default:
        return false;
    }
  }

  onSidebarItemSelected(item: MenuItem): void {
    if (item.route) {
      this.router.navigate([item.route]);
    }
  }
}