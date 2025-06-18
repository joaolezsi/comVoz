import { Component } from '@angular/core';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-with-sidebar-layout',
  standalone: true,
  imports: [CommonModule, SidebarComponent, RouterOutlet],
  templateUrl: './with-sidebar.layout.html',
  styleUrls: ['./with-sidebar.layout.scss']
})
export class WithSidebarLayout {}