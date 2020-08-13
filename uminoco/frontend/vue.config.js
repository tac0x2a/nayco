module.exports = {
  assetsDir: 'static',
  transpileDependencies: [
    'vuetify'
  ],
  devServer: {
    proxy: {
      "/api*" :{
        'target': 'http://' + process.env.API_HOST + ':5000'
      }
    }
  }
}