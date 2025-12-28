// 控制调试日志的开关
// import.meta.env.DEV 是 Vite 提供的环境变量，开发模式下为 true，生产构建下为 false
// 如果你想在任何时候强制开启或关闭，可以直接修改这里的 DEBUG 变量
const DEBUG = import.meta.env.DEV; 

export const logger = {
  log: (...args: any[]) => {
    if (DEBUG) {
      console.log(...args);
    }
  },
  warn: (...args: any[]) => {
    if (DEBUG) {
      console.warn(...args);
    }
  },
  error: (...args: any[]) => {
    if (DEBUG) {
      console.error(...args);
    }
  },
  info: (...args: any[]) => {
    if (DEBUG) {
      console.info(...args);
    }
  }
};

export default logger;
