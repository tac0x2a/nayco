
const axios = require('axios').default

export default {
  listTables (callback) {
    axios.get('/api/v1/table/').then((res) => {
      callback(res.data)
    })
  },
  tableDetail (tableName, callback) {
    axios.get('/api/v1/table/' + tableName).then((res) => {
      callback(res.data)
    })
  }
}
