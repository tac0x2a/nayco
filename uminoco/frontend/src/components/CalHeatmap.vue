<template>
  <div>

      <div v-show="max">
        <center>
          <div id="cal-heatmap"></div>
        </center>
        <!-- TODO: Fix cal-heatmap navigation bugs -->
        <!-- <v-btn id="prev" x-small color="primary" dark>&lt;</v-btn>
        <v-btn v-on:click="reset" id="reset" x-small color="primary" dark>now</v-btn>
        <v-btn id="next" x-small color="primary" dark>&gt;</v-btn> -->
      </div>
      <div v-show="!max">
        loading... {{this.failer}}
      </div>

  </div>
</template>

<script>
import Clickhouse from '@/api/clickhouse.js'
// import CalHeatMap from 'cal-heatmap'
import CalHeatMap from '@/assets/scripts/cal-heatmap.js'

var cal = null

export default {
  props: {
    tableName: String
  },
  data: () => ({
    max: 0,
    failer: null
  }),
  mounted() {
  },

  watch: {
    tableName: {
      handler() {
        Clickhouse.calHeatmapMax(this.tableName, res => {
          this.max = res.max
        },
        err => {
          this.failer = { error: err, message: err?.response?.data?.message }
        })
      },
      immediate: true
    },
    max: {
      handler() {
        cal = new CalHeatMap()

        const startAt = new Date()
        startAt.setMonth(startAt.getMonth() - 3)
        cal.init({
          cellSize: 12,
          domain: 'month',
          subdomain: 'day',
          domainLabelFormat: '%b',
          subDomainDateFormat: '%Y-%m-%d',
          subDomainTextFormat: '%d',
          start: startAt,
          formatNumber: (v) => v.toInt,
          range: 4,
          label: {
            position: 'bottom'
          },
          animationDuration: 100,
          data: '/api/v1/table/' + this.tableName + '/cal-heatmap?start={{t:start}}&end={{t:end}}',
          displayLegend: false,
          itemName: ['data', 'data'],
          previousSelector: '#prev',
          nextSelector: '#next',
          legend: [0, this.max * 0.2, this.max * 0.4, this.max * 0.6, this.max * 0.8, this.max],
          legendColors: ['#ecf5e2', '#232181']
        })
      }
    }
  },

  methods: {
    reset() {
      if (cal) {
        cal.rewind()
      }
    }
  }
}
</script>

<style>
  @import '../assets/styles/cal-heatmap.css'
</style>
