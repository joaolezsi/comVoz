import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { environment } from '../../environments/environment';
import { Router } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { NotificationService } from '../services/notification.service';

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  subItems?: MenuItem[];
}

@Component({
  selector: 'app-contatos',
  templateUrl: './contatos.component.html',
  styleUrls: ['./contatos.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, SidebarComponent, HttpClientModule, RouterModule]
})
export class ContatosComponent implements OnInit, OnDestroy {
  contatos: any[] = [];
  contatoForm: FormGroup;
  exibirFormulario: boolean = false;
  arquivoSelecionado: File | null = null;
  apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private router: Router,
    private notificationService: NotificationService
  ) {
    this.contatoForm = this.fb.group({
      nome: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      telefone: ['']
    });
  }

  ngOnInit(): void {
    this.carregarContatos();
    console.log('Componente de contatos inicializado');
  }

  // Método chamado quando o componente é destruído
  ngOnDestroy(): void {
    console.log('Componente de contatos destruído');
  }

  onSidebarItemSelected(item: MenuItem): void {
    if (item.label === 'Contatos') {
      this.carregarContatos();
    }
    if (item.route) {
      this.router.navigate([item.route]);
    }
  }

  // Método para obter o token JWT do localStorage
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  // Método para verificar se o usuário está autenticado
  private verificarAutenticacao(): boolean {
    const token = this.getToken();
    if (!token) {
      this.notificationService.error('Não Autenticado', 'Faça login para continuar.');
      setTimeout(() => {
        this.router.navigate(['/login']);
      }, 2000);
      return false;
    }
    return true;
  }

  carregarContatos(): void {
    if (!this.verificarAutenticacao()) return;

    console.log('Carregando contatos...');
    const token = this.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<any[]>(`${this.apiUrl}/contatos`, { headers })
      .subscribe({
        next: (data) => {
          this.contatos = data;
          console.log('Contatos carregados:', this.contatos.length);
        },
        error: (err) => {
          console.error('Erro ao carregar contatos', err);
          this.notificationService.error('Erro ao Carregar', 'Erro ao carregar contatos');
          if (err.status === 401) {
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
          }
        }
      });
  }

  toggleFormulario(): void {
    this.exibirFormulario = !this.exibirFormulario;
    if (!this.exibirFormulario) {
      this.contatoForm.reset();
    }
  }

  onFileSelected(event: Event): void {
    const element = event.target as HTMLInputElement;
    if (element.files && element.files.length > 0) {
      this.arquivoSelecionado = element.files[0];
    }
  }

  baixarModeloExcel(): void {
    // Conteúdo do arquivo CSV
    const csvContent = 'nome;email;telefone\npedro;p@gmail.com;\npedro;pe@gmail.com;3133333333';
    
    // Criar um Blob com o conteúdo CSV
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // Criar URL temporária para o Blob
    const url = window.URL.createObjectURL(blob);
    
    // Criar elemento <a> para download
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'modelo_contatos.csv');
    
    // Adicionar o link ao DOM, clicar nele e depois remover
    document.body.appendChild(link);
    link.click();
    
    // Limpar usando setTimeout para evitar problemas em alguns navegadores
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);
  }

  uploadArquivo(): void {
    if (!this.arquivoSelecionado) {
      this.notificationService.warning('Arquivo Necessário', 'Nenhum arquivo selecionado');
      return;
    }

    if (!this.verificarAutenticacao()) return;

    // Verificar se o arquivo é CSV, XLS ou XLSX
    const fileType = this.arquivoSelecionado.name.split('.').pop()?.toLowerCase();
    const allowedTypes = ['csv', 'xls', 'xlsx'];
    
    if (!fileType || !allowedTypes.includes(fileType)) {
      this.notificationService.error('Formato Inválido', 'Formato de arquivo inválido. Use apenas CSV, XLS ou XLSX.');
      return;
    }

    const token = this.getToken();
    const formData = new FormData();
    
    // Adiciona o arquivo com a chave 'file' exatamente como esperado pelo backend
    formData.append('file', this.arquivoSelecionado);
    
    console.log('Enviando arquivo:', this.arquivoSelecionado.name);
    console.log('Tipo do arquivo:', this.arquivoSelecionado.type);
    console.log('Tamanho do arquivo:', this.arquivoSelecionado.size, 'bytes');

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    // Mostra mensagem de carregamento
    this.notificationService.info('Enviando Arquivo', 'Enviando arquivo, aguarde...');

    this.http.post(`${this.apiUrl}/contatos/by_excel`, formData, { headers })
      .subscribe({
        next: (response: any) => {
          console.log('Resposta do servidor:', response);
          this.notificationService.success('Importação Concluída', 'Contatos importados com sucesso!');
          this.carregarContatos();
          this.arquivoSelecionado = null;
          const fileInput = document.getElementById('fileInput') as HTMLInputElement;
          if (fileInput) {
            fileInput.value = '';
          }
        },
        error: (err) => {
          console.error('Erro ao importar contatos:', err);
          
          // Informações de erro mais detalhadas
          if (err.status === 400) {
            this.notificationService.error('Erro no Arquivo', err.error?.error || 'Formato inválido ou dados incorretos');
          } else if (err.status === 401) {
            this.notificationService.error('Não Autorizado', 'Faça login novamente.');
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
          } else {
            this.notificationService.error('Erro na Importação', err.error?.error || 'Erro desconhecido');
          }
        }
      });
  }

  criarContato(): void {
    if (this.contatoForm.invalid) {
      this.notificationService.warning('Campos Obrigatórios', 'Preencha os campos obrigatórios');
      return;
    }

    // Verificar autenticação e obter token
    if (!this.verificarAutenticacao()) return;
    
    const token = this.getToken();
    console.log('Token JWT utilizado:', token);

    // Configurar cabeçalhos com o token JWT
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    // Obter valores do formulário e formatar no formato exato solicitado
    const contatoData = {
      nome: this.contatoForm.value.nome,
      email: this.contatoForm.value.email,
      telefone: this.contatoForm.value.telefone || ''
    };

    // Configuração para debug
    console.log('Headers:', headers);
    console.log('Enviando dados:', contatoData);

    // Fazer requisição POST com o token no cabeçalho
    this.http.post(`${this.apiUrl}/contatos`, contatoData, { headers })
      .subscribe({
        next: (response: any) => {
          console.log('Resposta da API:', response);
          this.notificationService.success('Contato Criado', 'Contato criado com sucesso!');
          this.carregarContatos();
          this.contatoForm.reset();
        },
        error: (err) => {
          console.error('Erro ao criar contato', err);
          this.notificationService.error('Erro ao Criar', err.error?.error || 'Erro desconhecido');
          
          // Se houver erro de autenticação, redirecionar para login
          if (err.status === 401) {
            setTimeout(() => {
              this.router.navigate(['/login']);
            }, 2000);
          }
        }
      });
  }
} 