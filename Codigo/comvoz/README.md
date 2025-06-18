# Documentação Técnica Frontend ComVoz - Versão Expandida

## 1. Arquitetura do Sistema

### 1.1 Tecnologias Principais
- **Framework**: Angular (Latest)
- **Estilização**: SCSS com Design System próprio
- **Gerenciamento de Estado**: Serviços Angular
- **Autenticação**: JWT Token
- **UI Components**: Material Design Icons + Componentes Customizados

### 1.2 Estrutura de Diretórios Detalhada
```
comvoz/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── shared/
│   │   │   └── specific/
│   │   ├── layouts/
│   │   │   ├── with-sidebar.layout
│   │   │   └── without-sidebar.layout
│   │   ├── services/
│   │   │   ├── auth.service
│   │   │   ├── pesquisa.service
│   │   │   └── plano.service
│   │   ├── guards/
│   │   │   └── auth.guard
│   │   ├── interfaces/
│   │   │   ├── user.interface
│   │   │   ├── pesquisa.interface
│   │   │   └── plano.interface
│   │   └── pages/
│   │       ├── home/
│   │       ├── login/
│   │       ├── pesquisas/
│   │       ├── questoes/
│   │       └── planos/
│   ├── assets/
│   │   ├── images/
│   │   └── icons/
│   └── styles/
│       ├── _variables.scss
│       ├── _mixins.scss
│       └── global.scss
```

## 2. Componentes do Sistema

### 2.1 Componente de Questões (`questoes.component`)

#### Estrutura
```typescript
interface Questao {
  tipo: 'multipla_escolha' | 'escala' | 'texto_livre';
  texto: string;
  opcoes?: string[];
  obrigatoria: boolean;
  ordem: number;
}
```

#### Funcionalidades Principais
- Criação de novas questões
- Edição de questões existentes
- Ordenação via drag-and-drop
- Validação de campos obrigatórios
- Preview em tempo real

#### Estilos Específicos
```scss
// Variáveis específicas do componente
$question-card-bg: #ffffff;
$question-border: 1px solid #e0e0e0;
$question-shadow: 0 2px 4px rgba(0,0,0,0.1);
```

### 2.2 Componente de Planos (`planos.component`)

#### Interface de Plano
```typescript
interface Plano {
  id: number;
  nome: string;
  descricao: string;
  valor: number;
  limite_pesquisas: number;
  limite_envios: number;
  recursos: string[];
}
```

#### Características
- Exibição de planos disponíveis
- Comparação de recursos
- Integração com sistema de pagamentos
- Upgrade/Downgrade de plano

#### Layout Responsivo
- Grid system adaptativo
- Breakpoints customizados
- Animações de hover e seleção

## 3. Serviços e Integrações

### 3.1 AuthService (Expandido)
```typescript
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Métodos principais
  login(email: string, password: string): Observable<User>;
  logout(): void;
  refreshToken(): Observable<string>;
  validateSession(): boolean;
  
  // Utilitários
  getAuthHeaders(): HttpHeaders;
  decodeToken(token: string): any;
  handleAuthError(error: HttpErrorResponse): Observable<never>;
}
```

### 3.2 PesquisaService
```typescript
@Injectable({
  providedIn: 'root'
})
export class PesquisaService {
  // CRUD Operations
  criarPesquisa(pesquisa: Pesquisa): Observable<Pesquisa>;
  obterPesquisas(filtros?: FiltrosPesquisa): Observable<Pesquisa[]>;
  atualizarPesquisa(id: string, dados: Partial<Pesquisa>): Observable<Pesquisa>;
  deletarPesquisa(id: string): Observable<void>;
  
  // Operações específicas
  duplicarPesquisa(id: string): Observable<Pesquisa>;
  exportarRespostas(id: string, formato: 'csv' | 'xlsx'): Observable<Blob>;
}
```

## 4. Sistema de Design

### 4.1 Tokens de Design
```scss
// Cores
$color-primary: #007bff;
$color-secondary: #0056b3;
$color-success: #28a745;
$color-danger: #dc3545;
$color-warning: #ffc107;

// Tipografia
$font-family-base: 'Roboto', sans-serif;
$font-size-base: 16px;
$line-height-base: 1.5;

// Espaçamento
$spacing-unit: 8px;
$spacing-small: $spacing-unit;
$spacing-medium: $spacing-unit * 2;
$spacing-large: $spacing-unit * 3;

// Breakpoints
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;
```

### 4.2 Componentes Reutilizáveis

#### Botões
```scss
.btn {
  &-primary { ... }
  &-secondary { ... }
  &-outline { ... }
  &-danger { ... }
  &-success { ... }
}
```

#### Cards
```scss
.card {
  &-default { ... }
  &-elevated { ... }
  &-interactive { ... }
}
```

## 5. Fluxos de Dados

### 5.1 Ciclo de Vida da Pesquisa
1. Criação da pesquisa (título, descrição)
2. Adição de questões
3. Configuração de envios
4. Ativação/publicação
5. Coleta de respostas
6. Geração de relatórios

### 5.2 Gerenciamento de Estado
```typescript
interface AppState {
  user: User | null;
  currentPesquisa: Pesquisa | null;
  planoAtual: Plano | null;
  notifications: Notification[];
}
```

## 6. Segurança e Performance

### 6.1 Medidas de Segurança
- XSS Protection
- CSRF Tokens
- Sanitização de inputs
- Rate Limiting
- Validação de dados

### 6.2 Otimizações
```typescript
// Exemplo de lazy loading
const routes: Routes = [
  {
    path: 'pesquisas',
    loadChildren: () => import('./pages/pesquisas/pesquisas.module')
      .then(m => m.PesquisasModule)
  }
];
```

## 7. Testes (Expandido)

### 7.1 Testes Unitários
```typescript
describe('QuestoesComponent', () => {
  let component: QuestoesComponent;
  let fixture: ComponentFixture<QuestoesComponent>;
  
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QuestoesComponent],
      providers: [
        { provide: PesquisaService, useValue: mockPesquisaService }
      ]
    }).compileComponents();
  });
  
  it('deve criar nova questão', () => {
    // implementação
  });
});
```

### 7.2 Testes E2E
```typescript
describe('Fluxo de Pesquisa', () => {
  it('deve criar e publicar pesquisa', () => {
    // implementação
  });
});
```

## 8. Guias de Desenvolvimento

### 8.1 Padrões de Código
- Prefixos de componentes: `app-`
- Nomenclatura de métodos: camelCase
- Interfaces: PascalCase
- Constantes: UPPER_SNAKE_CASE

### 8.2 Processo de Desenvolvimento
1. Criar branch feature
2. Desenvolver componente/feature
3. Testes unitários
4. Code review
5. Merge para develop

## 9. Monitoramento e Logs

### 9.1 Sistema de Logs
```typescript
class LogService {
  logError(error: Error, context?: string): void;
  logInfo(message: string, data?: any): void;
  logWarning(message: string, data?: any): void;
}
```

### 9.2 Métricas
- Tempo de carregamento
- Taxa de erro
- Uso de memória
- Performance de queries

## 10. Documentação de API

### 10.1 Endpoints Principais
```typescript
const API = {
  AUTH: {
    LOGIN: '/auth/login',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout'
  },
  PESQUISAS: {
    BASE: '/pesquisas',
    DETAIL: (id: string) => `/pesquisas/${id}`,
    RESPOSTAS: (id: string) => `/pesquisas/${id}/respostas`
  },
  PLANOS: {
    BASE: '/planos',
    UPGRADE: '/planos/upgrade'
  }
};
```

### 10.2 Respostas Padrão
```typescript
interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
  timestamp: string;
}
```

## 11. Processo de Deploy

### 11.1 Ambientes
- Development: `ng serve`
- Staging: `ng build --configuration=staging`
- Production: `ng build --configuration=production`

### 11.2 Variáveis de Ambiente
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://api.comvoz.com',
  version: '1.0.0',
  features: {
    enableAnalytics: true,
    enableNotifications: true
  }
};
```

Esta documentação expandida fornece uma visão mais detalhada e técnica do sistema, facilitando tanto a manutenção quanto o desenvolvimento de novas funcionalidades. Para atualizações ou esclarecimentos adicionais, consulte a equipe de desenvolvimento.
