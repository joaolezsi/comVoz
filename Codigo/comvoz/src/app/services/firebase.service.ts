import { Injectable } from '@angular/core';
import { initializeApp, FirebaseApp } from 'firebase/app';
import { getAnalytics, Analytics } from 'firebase/analytics';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class FirebaseService {
  private app: FirebaseApp;
  private analytics?: Analytics;

  constructor() {
    this.app = initializeApp(environment.firebase);
    
    // Inicializa o Analytics apenas em produção
    if (environment.production) {
      this.analytics = getAnalytics(this.app);
    }
  }

  getApp(): FirebaseApp {
    return this.app;
  }

  getAnalytics(): Analytics | undefined {
    return this.analytics;
  }
} 