# Sistema de Notificações ComVoz

Este sistema de notificações padronizado foi criado para substituir os `alert()` e outras mensagens não padronizadas em todo o sistema ComVoz, proporcionando uma experiência de usuário mais profissional e consistente.

## Características

- **Design Moderno**: Interface elegante com animações suaves
- **Responsivo**: Adapta-se a diferentes tamanhos de tela
- **Acessível**: Suporte a leitores de tela e navegação por teclado
- **Tipado**: Totalmente tipado com TypeScript
- **Flexível**: Suporte a diferentes tipos de notificação e ações personalizadas

## Tipos de Notificação

### 1. Sucesso (Success)
- **Cor**: Verde (#27ae60)
- **Ícone**: check_circle
- **Uso**: Operações concluídas com êxito

### 2. Erro (Error)
- **Cor**: Vermelho (#e74c3c)
- **Ícone**: error
- **Uso**: Erros críticos, falhas de operação

### 3. Aviso (Warning)
- **Cor**: Laranja (#f39c12)
- **Ícone**: warning
- **Uso**: Alertas, validações, dados incompletos

### 4. Informação (Info)
- **Cor**: Azul (#3498db)
- **Ícone**: info
- **Uso**: Informações gerais, dicas

## Como Usar

### 1. Injetar o Serviço

```typescript
import { NotificationService } from '../services/notification.service';

constructor(private notificationService: NotificationService) {}
```

### 2. Métodos Básicos

```typescript
// Notificação de sucesso (desaparece em 5s)
this.notificationService.success('Título', 'Mensagem de sucesso');

// Notificação de erro (não desaparece automaticamente)
this.notificationService.error('Título', 'Mensagem de erro');

// Notificação de aviso (desaparece em 7s)
this.notificationService.warning('Título', 'Mensagem de aviso');

// Notificação de informação (desaparece em 5s)
this.notificationService.info('Título', 'Mensagem informativa');
```

### 3. Métodos de Conveniência

```typescript
// Métodos simplificados (apenas mensagem)
this.notificationService.showSuccess('Operação realizada com sucesso!');
this.notificationService.showError('Erro ao processar solicitação');
this.notificationService.showWarning('Dados incompletos');
this.notificationService.showInfo('Nova funcionalidade disponível');
```

### 4. Métodos Específicos do ComVoz

```typescript
// Contextos específicos da aplicação
this.notificationService.showPesquisaCriada();
this.notificationService.showPesquisaAtualizada();
this.notificationService.showQuestaoAdicionada();
this.notificationService.showErroConexao();
this.notificationService.showLoginSucesso();
this.notificationService.showPlanoAlterado('Premium');
```

### 5. Notificações com Ações

```typescript
this.notificationService.success(
  'Interesse Registrado',
  'Nossa equipe entrará em contato em breve.',
  0, // Duração (0 = não remove automaticamente)
  [
    {
      label: 'Ver Contatos',
      action: () => this.router.navigate(['/contatos']),
      style: 'primary'
    },
    {
      label: 'Fechar',
      action: () => {},
      style: 'secondary'
    }
  ]
);
```

## Configurações Avançadas

### Duração Personalizada

```typescript
// Notificação que desaparece em 10 segundos
this.notificationService.success('Título', 'Mensagem', 10000);

// Notificação que não desaparece automaticamente
this.notificationService.error('Título', 'Mensagem', 0);
```

### Remoção Manual

```typescript
// Remover uma notificação específica
this.notificationService.removeNotification('notification-id');

// Remover todas as notificações
this.notificationService.clearAll();
```

## Exemplos de Uso por Contexto

### Login/Autenticação

```typescript
// Sucesso no login
this.notificationService.showLoginSucesso();

// Erro de credenciais
this.notificationService.error('Login Inválido', 'Email ou senha incorretos.');

// Sessão expirada
this.notificationService.error('Sessão Expirada', 'Faça login novamente.');
```

### Pesquisas

```typescript
// Pesquisa criada
this.notificationService.showPesquisaCriada();

// Pesquisa sem questões
this.notificationService.showPesquisaSemQuestoes();

// Questão adicionada
this.notificationService.showQuestaoAdicionada();
```

### Planos

```typescript
// Plano alterado
this.notificationService.showPlanoAlterado('Premium');

// Interesse registrado
this.notificationService.success(
  'Interesse Registrado',
  'Nossa equipe entrará em contato.',
  0,
  [{ label: 'Ver Contatos', action: () => this.router.navigate(['/contatos']) }]
);
```

### Relatórios

```typescript
// Relatório gerado
this.notificationService.showRelatorioGerado();

// Erro ao gerar relatório
this.notificationService.error('Erro no Relatório', 'Não foi possível gerar o relatório.');
```

## Boas Práticas

1. **Use títulos descritivos**: Seja claro sobre o que aconteceu
2. **Mensagens concisas**: Mantenha as mensagens curtas e objetivas
3. **Tipo apropriado**: Use o tipo correto para cada situação
4. **Ações relevantes**: Adicione ações apenas quando necessário
5. **Duração adequada**: Erros importantes não devem desaparecer automaticamente

## Substituindo Alerts Existentes

### Antes (❌)
```typescript
alert('Pesquisa criada com sucesso!');
alert('Erro ao carregar dados');
```

### Depois (✅)
```typescript
this.notificationService.showPesquisaCriada();
this.notificationService.showErroConexao();
```

## Integração no Projeto

O componente de notificação já está integrado no `app.component.html` e será exibido automaticamente em todas as páginas. Não é necessário adicionar o componente em cada página individual.

## Responsividade

O sistema se adapta automaticamente a diferentes tamanhos de tela:
- **Desktop**: Notificações no canto superior direito
- **Mobile**: Notificações ocupam toda a largura da tela
- **Tablet**: Layout intermediário otimizado

## Acessibilidade

- Suporte a leitores de tela
- Navegação por teclado
- Cores com contraste adequado
- Textos alternativos para ícones
- Opção de redução de movimento 