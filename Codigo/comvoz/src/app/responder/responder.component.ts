import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormBuilder, Validators, FormArray } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { environment } from '../../environments/environment';
import { NotificationService } from '../services/notification.service';

@Component({
  selector: 'app-responder',
  templateUrl: './responder.component.html',
  styleUrls: ['./responder.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule]
})
export class ResponderComponent implements OnInit {
  pesquisaId: string | null = null;
  pesquisa: any = null;
  formulario: FormGroup;
  carregando: boolean = true;
  enviado: boolean = false;
  erro: boolean = false;

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private notificationService: NotificationService
  ) {
    this.formulario = this.fb.group({
      nome: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      respostas: this.fb.group({})
    });
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.pesquisaId = params['id'];
      if (this.pesquisaId) {
        this.carregarPesquisa();
      } else {
        this.notificationService.error('Link Inválido', 'ID da pesquisa não fornecido.');
        this.erro = true;
        this.carregando = false;
      }
    });
  }

  carregarPesquisa(): void {
    if (!this.pesquisaId) return;

    this.http.get(`${environment.apiUrl}/pesquisas/${this.pesquisaId}`).subscribe({
      next: (data: any) => {
        console.log('Carregando pesquisa com ID:', this.pesquisaId);
        
        console.log('Dados da pesquisa recebidos:', data);
        console.log('Perguntas da pesquisa:', data.perguntas);
        
        data.perguntas.forEach((pergunta: any) => {
          console.log('Pergunta:', {
            id: pergunta.id,
            tipo: pergunta.tipo,
            texto: pergunta.texto
          });
        });
        
        this.pesquisa = data;
        this.inicializarFormularioRespostas();
        this.carregando = false;
      },
      error: (err) => {
        console.error('Erro ao carregar pesquisa:', err);
        this.carregando = false;
        this.erro = true;
        this.notificationService.error('Erro ao Carregar', 'Erro ao carregar pesquisa. Verifique o link ou tente novamente mais tarde.');
      }
    });
  }

  inicializarFormularioRespostas(): void {
    console.log('Inicializando formulário de respostas');
    console.log('Perguntas da pesquisa:', this.pesquisa.perguntas);
    
    const respostasGroup = this.fb.group({});
    
    this.pesquisa.perguntas.forEach((pergunta: any) => {
      console.log('Processando pergunta:', {
        id: pergunta.id,
        tipo: pergunta.tipo,
        texto: pergunta.texto
      });
      
      const controlName = pergunta.id.toString();
      console.log('Nome do controle:', controlName);
      
      if (pergunta.tipo === 'texto') {
        console.log('Criando controle de texto para pergunta:', pergunta.id);
        respostasGroup.addControl(controlName, this.fb.control('', [
          Validators.required,
          Validators.minLength(1)
        ]));
      } else {
        console.log('Criando controle para pergunta:', pergunta.id);
        respostasGroup.addControl(controlName, this.fb.control(null, [Validators.required]));
      }
    });

    this.formulario.setControl('respostas', respostasGroup);
    console.log('Formulário inicializado:', this.formulario.value);
    console.log('Controles do grupo de respostas:', Object.keys(respostasGroup.controls));
  }

  selecionarNPS(perguntaId: number, valor: number): void {
    console.log('Selecionando NPS:', { perguntaId, valor });
    const respostasGroup = this.formulario.get('respostas') as FormGroup;
    const controlName = perguntaId.toString();
    
    if (respostasGroup.contains(controlName)) {
      respostasGroup.get(controlName)?.setValue(valor);
      console.log('Valor do controle após seleção:', respostasGroup.get(controlName)?.value);
    } else {
      console.error(`Controle não encontrado para pergunta ${perguntaId}`);
      console.log('Controles disponíveis:', Object.keys(respostasGroup.controls));
    }
  }

  selecionarOpcao(perguntaId: number, opcaoId: number): void {
    console.log('Selecionando opção:', { perguntaId, opcaoId });
    const respostasGroup = this.formulario.get('respostas') as FormGroup;
    const controlName = perguntaId.toString();
    
    if (respostasGroup.contains(controlName)) {
      respostasGroup.get(controlName)?.setValue(opcaoId);
      console.log('Valor do controle após seleção:', respostasGroup.get(controlName)?.value);
    } else {
      console.error(`Controle não encontrado para pergunta ${perguntaId}`);
      console.log('Controles disponíveis:', Object.keys(respostasGroup.controls));
    }
  }

  verificarFormularioValido(): boolean {
    console.log('Verificando formulário...');
    
    const nomeValido = this.formulario.get('nome')?.valid;
    const emailValido = this.formulario.get('email')?.valid;
    
    console.log('Validação nome e email:', { nomeValido, emailValido });
    
    if (!nomeValido || !emailValido) {
      console.log('Nome ou email inválidos');
      return false;
    }

    const respostasGroup = this.formulario.get('respostas') as FormGroup;
    if (!respostasGroup) {
      console.log('Grupo de respostas não encontrado');
      return false;
    }

    console.log('Controles disponíveis:', Object.keys(respostasGroup.controls));

    const todasRespostasPreenchidas = Object.keys(respostasGroup.controls).every(key => {
      const control = respostasGroup.get(key);
      const valor = control?.value;
      const pergunta = this.pesquisa.perguntas.find((p: any) => p.id.toString() === key);
      
      let preenchido = false;
      if (pergunta.tipo === 'texto') {
        preenchido = valor !== null && valor !== undefined && valor.trim() !== '';
      } else {
        preenchido = valor !== null && valor !== undefined && valor !== '';
      }
      
      console.log(`Resposta ${key} (${pergunta.tipo}):`, { 
        valor, 
        preenchido,
        pergunta: pergunta.texto 
      });
      
      return preenchido;
    });

    console.log('Todas as respostas preenchidas:', todasRespostasPreenchidas);
    
    return nomeValido && emailValido && todasRespostasPreenchidas;
  }

  enviarFormulario(): void {
    if (!this.verificarFormularioValido()) {
      this.notificationService.warning('Campos Obrigatórios', 'Por favor, preencha todos os campos obrigatórios.');
      return;
    }

    this.carregando = true;
    this.notificationService.info('Enviando', 'Enviando resposta...');

    // Mapeia as respostas para o formato esperado pelo backend
    const respostasFormatadas = Object.entries(this.formulario.value.respostas).map(([perguntaId, valor]) => {
      const pergunta = this.pesquisa.perguntas.find((p: any) => p.id.toString() === perguntaId);
      
      // Mapeia o tipo da pergunta para o formato esperado pelo backend
      let tipoPergunta = pergunta.tipo;
      if (tipoPergunta === 'choice') {
        tipoPergunta = 'escolha';
      }
      
      return {
        pergunta_id: parseInt(perguntaId),
        resposta: valor,
        tipo_pergunta: tipoPergunta
      };
    });

    const dadosResposta = {
      respostas: respostasFormatadas,
      nome: this.formulario.value.nome,
      email: this.formulario.value.email,
      pesquisa_id: this.pesquisaId
    };

    console.log('=== DADOS DA RESPOSTA ===');
    console.log('Nome:', dadosResposta.nome);
    console.log('Email:', dadosResposta.email);
    console.log('Pesquisa ID:', dadosResposta.pesquisa_id);
    console.log('Respostas:');
    dadosResposta.respostas.forEach((resposta, index) => {
      console.log(`Resposta ${index + 1}:`, {
        pergunta_id: resposta.pergunta_id,
        resposta: resposta.resposta,
        tipo_pergunta: resposta.tipo_pergunta
      });
    });
    console.log('=======================');

    // Log do objeto completo para teste no Postman
    console.log('=== OBJETO COMPLETO PARA POSTMAN ===');
    console.log(JSON.stringify(dadosResposta, null, 2));
    console.log('===================================');

    this.http.post(`${environment.apiUrl}/respostas`, dadosResposta).subscribe({
      next: (response: any) => {
        console.log('Resposta enviada com sucesso:', response);
        this.carregando = false;
        this.enviado = true;
        this.notificationService.success('Resposta Enviada', 'Obrigado! Sua resposta foi enviada com sucesso.');
      },
      error: (err) => {
        console.error('Erro ao enviar resposta:', err);
        this.carregando = false;
        this.erro = true;
        this.notificationService.error('Erro no Envio', 'Erro ao enviar resposta. Por favor, tente novamente mais tarde.');
      }
    });
  }
} 