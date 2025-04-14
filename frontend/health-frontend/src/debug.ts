// 调试文件，用于输出环境变量
console.log('环境变量:');
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('BASE_URL:', import.meta.env.BASE_URL);
console.log('MODE:', import.meta.env.MODE);
console.log('DEV:', import.meta.env.DEV);
console.log('PROD:', import.meta.env.PROD);
console.log('SSR:', import.meta.env.SSR);

// 导出一个空对象，以便可以被导入
export default {}; 