import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number; // em milissegundos, 0 = não remove automaticamente
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: () => void;
  style?: 'primary' | 'secondary';
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  public notifications$: Observable<Notification[]> = this.notificationsSubject.asObservable();

  constructor() { }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private addNotification(notification: Notification): void {
    const currentNotifications = this.notificationsSubject.value;
    this.notificationsSubject.next([...currentNotifications, notification]);

    // Remove automaticamente após o tempo especificado
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        this.removeNotification(notification.id);
      }, notification.duration);
    }
  }

  // Métodos públicos para diferentes tipos de notificação
  success(title: string, message: string, duration: number = 5000, actions?: NotificationAction[]): void {
    const notification: Notification = {
      id: this.generateId(),
      type: 'success',
      title,
      message,
      duration,
      actions
    };
    this.addNotification(notification);
  }

  error(title: string, message: string, duration: number = 0, actions?: NotificationAction[]): void {
    const notification: Notification = {
      id: this.generateId(),
      type: 'error',
      title,
      message,
      duration,
      actions
    };
    this.addNotification(notification);
  }

  warning(title: string, message: string, duration: number = 7000, actions?: NotificationAction[]): void {
    const notification: Notification = {
      id: this.generateId(),
      type: 'warning',
      title,
      message,
      duration,
      actions
    };
    this.addNotification(notification);
  }

  info(title: string, message: string, duration: number = 5000, actions?: NotificationAction[]): void {
    const notification: Notification = {
      id: this.generateId(),
      type: 'info',
      title,
      message,
      duration,
      actions
    };
    this.addNotification(notification);
  }

  // Remove uma notificação específica
  removeNotification(id: string): void {
    const currentNotifications = this.notificationsSubject.value;
    const filteredNotifications = currentNotifications.filter(n => n.id !== id);
    this.notificationsSubject.next(filteredNotifications);
  }

  // Remove todas as notificações
  clearAll(): void {
    this.notificationsSubject.next([]);
  }

  // Métodos de conveniência para casos comuns
  showSuccess(message: string): void {
    this.success('Sucesso', message);
  }

  showError(message: string): void {
    this.error('Erro', message);
  }

  showWarning(message: string): void {
    this.warning('Atenção', message);
  }

  showInfo(message: string): void {
    this.info('Informação', message);
  }

  // Métodos específicos para o contexto do ComVoz
  showPesquisaCriada(): void {
    this.success('Pesquisa Criada', 'Sua pesquisa foi criada com sucesso e está pronta para ser compartilhada.');
  }

  showPesquisaAtualizada(): void {
    this.success('Pesquisa Atualizada', 'As alterações foram salvas com sucesso.');
  }

  showPesquisaExcluida(): void {
    this.success('Pesquisa Excluída', 'A pesquisa foi removida permanentemente.');
  }

  showQuestaoAdicionada(): void {
    this.success('Questão Adicionada', 'A nova questão foi adicionada à pesquisa.');
  }

  showErroConexao(): void {
    this.error('Erro de Conexão', 'Não foi possível conectar ao servidor. Verifique sua conexão de internet.');
  }

  showErroValidacao(campo: string): void {
    this.warning('Dados Incompletos', `Por favor, preencha o campo "${campo}" corretamente.`);
  }

  showPesquisaSemQuestoes(): void {
    this.warning('Pesquisa Incompleta', 'Adicione pelo menos uma questão antes de salvar a pesquisa.');
  }

  showLoginSucesso(): void {
    this.success('Login Realizado', 'Bem-vindo ao ComVoz!');
  }

  showLogoutSucesso(): void {
    this.info('Logout Realizado', 'Você foi desconectado com sucesso.');
  }

  showPlanoAlterado(novoPlano: string): void {
    this.success('Plano Alterado', `Seu plano foi alterado para ${novoPlano} com sucesso.`);
  }

  showRelatorioGerado(): void {
    this.success('Relatório Gerado', 'O relatório foi gerado e está sendo baixado.');
  }
} 