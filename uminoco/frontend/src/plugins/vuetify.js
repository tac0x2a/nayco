import Vue from 'vue'
import Vuetify from 'vuetify/lib'

Vue.use(Vuetify)

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#3c8cc4',
        secondary: '#3f51b5',
        accent: '#ff9800',
        error: '#ff5722',
        warning: '#ffc107',
        info: '#607d8b',
        success: '#8bc34a'
      }
    }
  }
})
