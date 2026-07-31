const translations = {
  en: {
    navFeatures: "Features",
    heroTitle: "Caching,<br>without the server.",
    heroBody:
      "A tiny, thread-safe in-memory cache for Python with TTL expiration and LRU eviction.",
    viewGithub: "View on GitHub",
    readDocs: "Read the docs",
    copy: "Copy",
    copied: "Copied",
    ready: "cache ready",
    manifesto:
      "The fast path should be the simple path. Keep hot data inside your process with predictable expiration and bounded memory.",
    threadSafe: "Thread-safe",
    threadBody:
      "An RLock protects every operation, including atomic counters and batch writes.",
    ttlTitle: "TTL expiration",
    ttlBody:
      "Set a default lifetime or tune individual keys. Expired values disappear lazily or on cleanup.",
    lruTitle: "LRU eviction",
    lruBody:
      "Bound memory by item count. Recently used values stay close while colder entries make room.",
    zeroTitle: "Zero dependencies",
    zeroBody:
      "One focused Python package. No service, connection pool, protocol, or runtime dependency.",
    apiTitle: "Small API.<br>Useful primitives.",
    apiBody:
      "Familiar operations cover the common cache lifecycle without turning your application into infrastructure.",
    setLabel: "store conditionally",
    getLabel: "read and refresh LRU",
    touchLabel: "extend lifetime",
    incrLabel: "count atomically",
    statsLabel: "observe behavior",
    lifecycleTitle: "Bounded by design.",
    lifecycleBody:
      "TTL clears stale values. LRU creates space under pressure. Both are deterministic, visible, and easy to reason about.",
    closingTitle: "Keep hot data close.",
    closingBody: "Install litecache and ship the fast path today.",
    footerText: "MIT licensed. Built for the Python community.",
  },
  zh: {
    navFeatures: "特性",
    heroTitle: "缓存加速，<br>无需服务器。",
    heroBody: "小巧、线程安全的 Python 进程内缓存，内置 TTL 过期与 LRU 淘汰。",
    viewGithub: "前往 GitHub",
    readDocs: "阅读文档",
    copy: "复制",
    copied: "已复制",
    ready: "缓存就绪",
    manifesto:
      "快速路径也应该是简单路径。将热点数据留在进程内，以可预期的过期策略控制内存边界。",
    threadSafe: "线程安全",
    threadBody: "RLock 保护每项操作，包括原子计数和批量写入。",
    ttlTitle: "TTL 过期",
    ttlBody: "设置全局默认生命周期，也可单独调整键；过期值支持惰性清理和主动清理。",
    lruTitle: "LRU 淘汰",
    lruBody: "按条目数量限制内存；常用数据保持活跃，冷数据自动让出空间。",
    zeroTitle: "零依赖",
    zeroBody: "一个专注的 Python 包，无服务、连接池、网络协议或运行时依赖。",
    apiTitle: "API 很小，<br>能力刚刚好。",
    apiBody: "熟悉的操作覆盖常见缓存生命周期，无需把应用变成基础设施项目。",
    setLabel: "按条件写入",
    getLabel: "读取并刷新 LRU",
    touchLabel: "延长生命周期",
    incrLabel: "原子计数",
    statsLabel: "观察缓存行为",
    lifecycleTitle: "边界清晰，可控可知。",
    lifecycleBody: "TTL 清除陈旧值，LRU 在压力下腾出空间；行为确定、状态可见、易于理解。",
    closingTitle: "让热点数据近在手边。",
    closingBody: "安装 litecache，立即交付更快路径。",
    footerText: "MIT 开源协议，为 Python 社区而构建。",
  },
};

let language = "en";
const languageButton = document.querySelector(".language");

function renderLanguage(nextLanguage) {
  language = nextLanguage;
  document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  const copy = translations[language];

  document.querySelectorAll("[data-copy]").forEach((element) => {
    const key = element.dataset.copy;
    if (copy[key]) {
      element.innerHTML = copy[key];
    }
  });

  languageButton.textContent = language === "en" ? "中文" : "EN";
  languageButton.setAttribute(
    "aria-label",
    language === "en" ? "切换到中文" : "Switch to English",
  );
  document.querySelector(".button.secondary").href =
    language === "en" ? "../README.md" : "../README.zh-CN.md";
}

languageButton.addEventListener("click", () => {
  renderLanguage(language === "en" ? "zh" : "en");
});

async function copyText(button, value) {
  try {
    await navigator.clipboard.writeText(value);
    const originalKey = button.dataset.copy;
    button.textContent = translations[language].copied;
    window.setTimeout(() => {
      button.textContent = translations[language][originalKey];
    }, 1300);
  } catch {
    button.textContent = value;
  }
}

document.querySelector(".copy-code").addEventListener("click", (event) => {
  copyText(event.currentTarget, document.querySelector("pre").innerText);
});

document.querySelector(".copy-install").addEventListener("click", (event) => {
  copyText(event.currentTarget, "pip install litecache");
});
