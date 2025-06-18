import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-without-sidebar-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  templateUrl: './without-sidebar.layout.html',
  styleUrls: ['./without-sidebar.layout.scss']
})
export class WithoutSidebarLayout {}