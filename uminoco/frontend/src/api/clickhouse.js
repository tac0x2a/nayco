
const axios = require('axios').default

export default {
  listTables (callback) {
    axios.get('/api/v1/table/').then((res) => {
      callback(res.data)
    })
  },
  tableDetail (tableName, callback, errorCallback) {
    axios.get('/api/v1/table/' + tableName).then((res) => {
      callback(res.data)
    }).catch((err) => {
      errorCallback(err)
    })
  }
}
