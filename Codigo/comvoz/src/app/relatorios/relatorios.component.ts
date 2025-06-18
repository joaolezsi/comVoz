import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { RelatorioService } from '../services/relatorio.service';
import { NotificationService } from '../services/notification.service';

interface PesquisaEstatisticas {
  id: string;
  titulo: string;
  respostas: number;
  taxaConversao: number;
  respostasPorAlternativa: any[];
  distribuicaoRespostas: any[];
}

@Component({
  selector: 'app-relatorios',
  standalone: true,
  imports: [CommonModule, RouterModule, HttpClientModule, FormsModule, SidebarComponent],
  templateUrl: './relatorios.component.html',
  styleUrls: ['./relatorios.component.scss']
})
export class RelatoriosComponent implements OnInit {
  pesquisaId: string | null = null;
  estatisticas: PesquisaEstatisticas | null = null;
  carregando: boolean = false;
  erro: string = '';

  constructor(
    private relatorioService: RelatorioService,
    private route: ActivatedRoute,
    private router: Router,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.pesquisaId = params['id'];
      if (this.pesquisaId) {
        this.carregarEstatisticas();
      } else {
        this.erro = 'ID de pesquisa não fornecido';
      }
    });
  }

  carregarEstatisticas(): void {
    if (!this.pesquisaId) return;

    this.carregando = true;
    this.erro = '';

    this.relatorioService.getEstatisticasPesquisa(this.pesquisaId)
      .subscribe({
        next: (data) => {
          this.estatisticas = {
            id: this.pesquisaId!,
            titulo: 'Pesquisa ' + this.pesquisaId,
            ...data
          };
          this.carregando = false;
        },
        error: (error) => {
          console.error('Erro ao carregar estatísticas:', error);
          this.notificationService.error('Erro ao Carregar', 'Não foi possível carregar as estatísticas. Tente novamente mais tarde.');
          this.carregando = false;
        }
      });
  }

  navegarParaDetalhes(perguntaId: string): void {
    this.router.navigate(['/relatorios/questao', this.pesquisaId, perguntaId]);
  }

  getMaxDistribuicao(): number {
    if (!this.estatisticas?.distribuicaoRespostas || this.estatisticas.distribuicaoRespostas.length === 0) {
      return 1; // Valor padrão para evitar divisão por zero
    }
    
    // Encontra o valor máximo entre todos os itens da distribuição
    return Math.max(...this.estatisticas.distribuicaoRespostas.map(item => item.valor));
  }

  exportarPDF(): void {
    if (!this.pesquisaId) return;

    this.carregando = true;
    this.relatorioService.gerarRelatorioPDF(this.pesquisaId)
      .subscribe({
        next: (blob) => {
          // Cria um URL para o blob e faz o download
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `relatorio-pesquisa-${this.pesquisaId}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
          this.carregando = false;
          this.notificationService.showRelatorioGerado();
        },
        error: (error) => {
          console.error('Erro ao exportar PDF:', error);
          this.notificationService.error('Erro na Exportação', 'Não foi possível exportar o relatório em PDF. Tente novamente mais tarde.');
          this.carregando = false;
        }
      });
  }

  voltarParaPesquisas(): void {
    this.router.navigate(['/pesquisas']);
  }
} 