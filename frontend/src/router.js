import { createRouter, createWebHistory } from 'vue-router'
import JobsView from './views/JobsView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'jobs', component: JobsView, meta: { title: 'Jobs' } },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('./views/AnalyticsView.vue'),
      meta: { title: 'Analytics' },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
