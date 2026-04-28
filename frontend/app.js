  const container = $('#message-container');
  if (!container) return;

  // 映射类型：error → danger
  const cssType = type === 'error' ? 'error' : type === 'danger' ? 'error' : type;

  const msg = document.createElement('div');
  msg.className = `message message--${cssType}`;
  msg.textContent = text;
  container.appendChild(msg);

  // 触发动画
  requestAnimationFrame(() => {
    msg.style.opacity = '1';
  });

  setTimeout(() => {
    msg.classList.add('message--fade-out');
    setTimeout(() => msg.remove(), 300);
  },

  updateUI() {
    const loginSection = $('#login-section');
    const dashboard = $('#dashboard');
    const logoutBtn = $('#logout-btn');

    if (this.isAuthenticated()) {
      if (loginSection) loginSection.style.display = 'none';
      if (dashboard) dashboard.style.display = 'block';
      if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
      if (loginSection) loginSection.style.display = 'block';
      if (dashboard) dashboard.style.display = 'none';
      if (logoutBtn) logoutBtn.style.display = 'none';
    }
// ============================================================

async function checkServerHealth() {
  const statusEl = $('#server-status');
  if (!statusEl) return;

  try {
    const response = await fetch('http://localhost:8000/health');
    const data = await response.json();

    if (response.ok && data.status === 'healthy') {
      statusEl.textContent = '● 服务器运行正常';
      statusEl.className = 'status-badge status-badge--success';
    } else {
      statusEl.textContent = '● 服务异常';
      statusEl.className = 'status-badge status-badge--error';
    }
  } catch {
    statusEl.textContent = '● 无法连接服务器';
    statusEl.className = 'status-badge status-badge--error';
  }
}


function bindEvents() {
  // 登录表单
  const loginForm = $('#login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
    const container = $('#queue-stats');
    if (!container) return;

    // 更新已有 stat-card 的值，而不是重新创建整个结构
    const cards = container.querySelectorAll('.stat-card');
    const values = [
      { value: stats.queue_size ?? '-', label: '队列大小' },
      { value: stats.total_sent ?? '-', label: '已发送' },
      { value: stats.total_received ?? '-', label: '已接收' },
      { value: stats.total_acked ?? '-', label: '已确认' },
      { value: stats.total_rejected ?? '-', label: '已拒绝' },
      { value: stats.consumer_running ? '运行中' : '已停止', label: '消费者状态' },
    ];

    values.forEach((item, index) => {
      if (cards[index]) {
        const valueEl = cards[index].querySelector('.stat-card__value');
        const labelEl = cards[index].querySelector('.stat-card__label');
        if (valueEl) valueEl.textContent = item.value;
        if (labelEl) labelEl.textContent = item.label;
      }
    });
  } catch (err) {
    showMessage('获取队列统计失败', 'error');
  }
