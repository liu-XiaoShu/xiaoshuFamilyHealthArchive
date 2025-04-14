// 记录相关API请求封装
export const getHealthOverview = async () => {
  // 模拟API响应
  console.log('获取健康概览数据');
  return {
    data: {
      physical_stats: {
        height: 170,
        weight: 65,
        blood_pressure: '120/80',
        blood_pressure_status: 'normal',
        blood_sugar: 5.2,
        blood_sugar_status: 'normal',
        last_exam_date: '2023-12-15'
      }
    }
  };
};

export const getRecordsList = async (type) => {
  // 模拟API响应
  console.log('获取记录列表', type);
  return {
    data: [
      {
        id: 1,
        title: '年度体检',
        date: '2023-12-15',
        record_type: 'physical',
        status: 'completed'
      },
      {
        id: 2,
        title: '感冒就诊',
        date: '2023-11-20',
        record_type: 'medical',
        status: 'completed'
      },
      {
        id: 3,
        title: '流感疫苗',
        date: '2023-10-05',
        record_type: 'vaccination',
        status: 'completed'
      }
    ]
  };
};

export const getPhysicalExamReport = async (reportId) => {
  // 模拟API响应
  console.log('获取体检报告', reportId);
  return {
    id: reportId,
    exam_id: '039121240427364',
    exam_date: '2024-04-27',
    user_name: '刘述瑶',
    age: 32,
    gender: '女',
    height: 163.5,
    weight: 57.3,
    blood_pressure: '120/80',
    abnormal_items: [
      {
        name: '嗜酸性粒细胞值偏高',
        severity: 'mild',
        description: '',
        suggestion: '定期复查血常规。',
        position: { top: 25, left: 30 }
      },
      {
        name: '肝囊肿',
        severity: 'moderate',
        description: '',
        suggestion: '定期复查肝脏彩超。',
        position: { top: 45, left: 25 }
      }
    ]
  };
};

// 模拟API请求
// 适用于开发环境

/**
 * 获取健康记录数据
 * @returns {Promise} 健康记录数据
 */
export async function getHealthRecords() {
  // 模拟网络请求延迟
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 返回模拟数据
  return {
    code: 200,
    message: 'success',
    data: {
      bloodPressure: {
        systolic: 120,
        diastolic: 80,
        pulse: 72,
        lastUpdate: '2025-04-01 08:30:00'
      },
      bloodSugar: {
        fasting: 5.2,
        afterMeal: 6.8,
        lastUpdate: '2025-04-01 08:00:00'
      },
      weight: {
        current: 65,
        target: 60,
        bmi: 22.5,
        lastUpdate: '2025-04-01 07:30:00'
      },
      sleep: {
        duration: 7.5,
        quality: 'good',
        lastUpdate: '2025-04-01 07:00:00'
      },
      activity: {
        steps: 8000,
        calories: 350,
        duration: 45,
        lastUpdate: '2025-03-31 21:00:00'
      }
    }
  }
}

/**
 * 获取最近记录列表
 * @param {string} type 记录类型
 * @returns {Promise} 记录列表
 */
export async function getRecentRecords(type = 'all') {
  // 模拟网络请求延迟
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // 基础记录数据
  const records = [
    {
      id: '1',
      title: '年度体检报告',
      type: 'physical',
      date: '2025-03-15',
      status: 'completed',
      summary: '总体健康状况良好，有轻微血压偏高情况',
      doctor: '张医生',
      hospital: '仁爱医院'
    },
    {
      id: '2',
      title: '牙齿检查',
      type: 'dental',
      date: '2025-03-10',
      status: 'completed',
      summary: '牙龈健康，需要定期洁牙',
      doctor: '李医生',
      hospital: '康健口腔诊所'
    },
    {
      id: '3',
      title: '血常规检查',
      type: 'blood',
      date: '2025-03-01',
      status: 'completed',
      summary: '各项指标正常',
      doctor: '王医生',
      hospital: '仁爱医院'
    },
    {
      id: '4',
      title: '眼科检查',
      type: 'eye',
      date: '2025-02-20',
      status: 'completed',
      summary: '近视度数增加50度，建议减少用眼时间',
      doctor: '刘医生',
      hospital: '明视眼科医院'
    },
    {
      id: '5',
      title: '心脏检查',
      type: 'heart',
      date: '2025-02-10',
      status: 'completed',
      summary: '心功能正常，注意控制血压',
      doctor: '赵医生',
      hospital: '心脏专科医院'
    }
  ]
  
  // 根据类型过滤
  let filteredRecords = records
  if (type !== 'all') {
    filteredRecords = records.filter(record => record.type === type)
  }
  
  // 返回模拟数据
  return {
    code: 200,
    message: 'success',
    data: filteredRecords
  }
}

/**
 * 获取报告详情
 * @param {string} reportId 报告ID
 * @returns {Promise} 报告详情
 */
export async function getReportDetails(reportId) {
  // 模拟网络请求延迟
  await new Promise(resolve => setTimeout(resolve, 800))
  
  // 模拟报告数据
  const report = {
    id: reportId,
    title: '2025年年度体检报告',
    date: '2025-03-15',
    hospital: '仁爱医院',
    doctor: '张医生',
    department: '体检中心',
    status: 'completed',
    summary: '总体健康状况良好，建议定期复查',
    items: [
      { name: '身高', value: '165cm', status: 'normal', reference: '正常' },
      { name: '体重', value: '55kg', status: 'normal', reference: '正常' },
      { name: 'BMI', value: '20.2', status: 'normal', reference: '18.5-24.9' },
      { name: '血压', value: '130/85mmHg', status: 'warning', reference: '120/80mmHg' },
      { name: '血糖', value: '5.8mmol/L', status: 'normal', reference: '3.9-6.1mmol/L' },
      { name: '总胆固醇', value: '5.5mmol/L', status: 'warning', reference: '<5.2mmol/L' },
      { name: '心率', value: '72bpm', status: 'normal', reference: '60-100bpm' }
    ],
    recommendations: [
      '控制饮食，减少高脂肪、高盐分食物摄入',
      '每周进行3-5次中等强度运动，每次30分钟以上',
      '保持良好作息习惯，确保充足睡眠',
      '6个月后复查血压和血脂'
    ],
    attachments: [
      { name: '心电图报告.pdf', url: '#', size: '2.5MB' },
      { name: 'B超检查报告.pdf', url: '#', size: '3.8MB' },
      { name: '血常规检查结果.pdf', url: '#', size: '1.2MB' }
    ]
  }
  
  // 返回模拟数据
  return {
    code: 200,
    message: 'success',
    data: report
  }
} 