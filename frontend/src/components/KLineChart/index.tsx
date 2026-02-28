import { useEffect, useRef, useState } from 'react'

let chartLibrary: any = null

interface KLineChartProps {
  data: Array<{
    time: number
    open: number | string
    high: number | string
    low: number | string
    close: number | string
    volume?: number
  }>
  height?: number
}

function KLineChart({ data, height = 500 }: KLineChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    let chart: any = null

    const initChart = async () => {
      if (!chartContainerRef.current) return

      try {
        if (!chartLibrary) {
          chartLibrary = await import('lightweight-charts')
        }

        const { createChart } = chartLibrary

        chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth,
          height: height,
          layout: {
            backgroundColor: '#ffffff',
            textColor: '#333333',
          },
          grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
          },
          rightPriceScale: {
            borderColor: '#dddddd',
          },
          timeScale: {
            borderColor: '#dddddd',
          },
        })

        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#ff0000',
          downColor: '#00ff00',
          borderUpColor: '#ff0000',
          borderDownColor: '#00ff00',
          wickUpColor: '#ff0000',
          wickDownColor: '#00ff00',
        })

        const volumeSeries = chart.addHistogramSeries({
          color: '#26a69a',
          priceFormat: { type: 'volume' },
          priceScaleId: '',
        })
        volumeSeries.priceScale().applyOptions({
          scaleMargins: { top: 0.8, bottom: 0 },
        })

        if (data && data.length > 0) {
          const candlestickData = data.map((item) => ({
            time: (item.time / 1000),
            open: typeof item.open === 'string' ? parseFloat(item.open) : item.open,
            high: typeof item.high === 'string' ? parseFloat(item.high) : item.high,
            low: typeof item.low === 'string' ? parseFloat(item.low) : item.low,
            close: typeof item.close === 'string' ? parseFloat(item.close) : item.close,
          }))

          const volumeData = data.map((item) => {
            const open = typeof item.open === 'string' ? parseFloat(item.open) : item.open
            const close = typeof item.close === 'string' ? parseFloat(item.close) : item.close
            const isUp = close >= open
            return {
              time: (item.time / 1000),
              value: item.volume || 0,
              color: isUp ? 'rgba(255, 0, 0, 0.5)' : 'rgba(0, 255, 0, 0.5)',
            }
          })

          candlestickSeries.setData(candlestickData)
          volumeSeries.setData(volumeData)
          chart.timeScale().fitContent()
        }

        const handleResize = () => {
          if (chartContainerRef.current && chart) {
            chart.applyOptions({ width: chartContainerRef.current.clientWidth })
          }
        }
        window.addEventListener('resize', handleResize)

        return () => {
          window.removeEventListener('resize', handleResize)
          if (chart) {
            chart.remove()
          }
        }
      } catch (err: any) {
        console.error('Chart init error:', err)
        setError(err.message || 'Failed to initialize chart')
      }
    }

    initChart()

    return () => {
      if (chart) {
        chart.remove()
      }
    }
  }, [data, height])

  if (error) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
        图表加载失败: {error}
      </div>
    )
  }

  return (
    <div ref={chartContainerRef} style={{ width: '100%', height }} />
  )
}

export default KLineChart
