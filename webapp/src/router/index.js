import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/TextReportView.vue')
  },
  {
    path: '/multimodal',
    name: 'Multimodal',
    component: () => import('../views/MultimodalView.vue')
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('../views/CompareView.vue')
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: () => import('../views/QuestionnaireView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router