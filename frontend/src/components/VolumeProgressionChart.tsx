import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
} from 'chart.js';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface VolumeData {
  muscle_name: string;
  total_volume: number;
  exercise_count: number;
  date: string;
  week_start: string;
}

interface Props {
  data: VolumeData[];
}

const VolumeProgressionChart: React.FC<Props> = ({ data }) => {
  // Group data by week_start and sum volumes for each muscle
  const weeklyData = data.reduce((acc: { [key: string]: { [key: string]: number } }, curr) => {
    const weekStart = curr.week_start;
    if (!acc[weekStart]) {
      acc[weekStart] = {};
    }
    if (!acc[weekStart][curr.muscle_name]) {
      acc[weekStart][curr.muscle_name] = 0;
    }
    acc[weekStart][curr.muscle_name] += curr.total_volume;
    return acc;
  }, {});

  // Get unique muscle names and weeks
  const muscles = Array.from(new Set(data.map(d => d.muscle_name)));
  const weeks = Object.keys(weeklyData).sort();

  // Prepare chart data
  const chartData: ChartData<'line'> = {
    labels: weeks.map(week => format(new Date(week), 'MMM d')),
    datasets: muscles.map((muscle, index) => ({
      label: muscle,
      data: weeks.map(week => weeklyData[week][muscle] || 0),
      borderColor: `hsl(${(index * 360) / muscles.length}, 70%, 50%)`,
      backgroundColor: `hsla(${(index * 360) / muscles.length}, 70%, 50%, 0.5)`,
      tension: 0.4,
    })),
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Weekly Volume Progression by Muscle',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Total Volume',
        },
      },
    },
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default VolumeProgressionChart;
