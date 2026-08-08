<script>
export default {
  onLaunch() {},
}
</script>

<style>
page {
  min-height: 100%;
  background: #f4f6f5;
  color: #1d2421;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 28rpx;
}
view, text, input, textarea, button { box-sizing: border-box; }
button { margin: 0; letter-spacing: 0; }
button::after { border: 0; }
.page-shell { min-height: 100vh; padding: 28rpx 28rpx calc(160rpx + env(safe-area-inset-bottom)); }
.page-content { width: 100%; max-width: 1080px; margin: 0 auto; }
.panel { background: #fff; border: 1px solid #e0e5e2; border-radius: 8px; padding: 32rpx; }
.section-title { display: block; margin-bottom: 10rpx; color: #1d2421; font-size: 36rpx; font-weight: 700; line-height: 1.35; }
.section-note { display: block; color: #6a746f; font-size: 26rpx; line-height: 1.65; }
.field-label { display: block; margin-bottom: 14rpx; color: #38413d; font-size: 26rpx; font-weight: 600; }
.input-control, .textarea-control { width: 100%; border: 1px solid #cfd7d3; border-radius: 6px; background: #fbfcfb; color: #1d2421; font-size: 28rpx; }
.input-control { height: 88rpx; padding: 0 24rpx; }
.textarea-control { min-height: 180rpx; padding: 22rpx 24rpx; line-height: 1.65; }
.input-control:focus, .textarea-control:focus { border-color: #16836b; background: #fff; }
.primary-button, .secondary-button, .danger-button { display: flex; min-height: 88rpx; align-items: center; justify-content: center; gap: 12rpx; border-radius: 6px; padding: 0 28rpx; font-size: 28rpx; font-weight: 650; line-height: 1.2; }
.primary-button { background: #167861; color: #fff; }
.primary-button[disabled] { background: #9bb4ab; color: #eef3f1; }
.secondary-button { border: 1px solid #bfc9c4; background: #fff; color: #26312c; }
.danger-button { border: 1px solid #e5b7b1; background: #fff8f7; color: #b74638; }
.form-group { margin-top: 30rpx; }
.status-message { margin-top: 24rpx; border-left: 6rpx solid #16836b; background: #edf7f3; padding: 22rpx 24rpx; color: #285a4d; font-size: 26rpx; line-height: 1.6; }
.status-message.error { border-left-color: #c85244; background: #fff2f0; color: #9d3b31; }
.segmented-control { display: grid; gap: 8rpx; border: 1px solid #dbe1de; border-radius: 7px; background: #edf1ef; padding: 8rpx; }
.segment-item { display: flex; min-height: 68rpx; align-items: center; justify-content: center; border-radius: 5px; color: #59645f; font-size: 26rpx; font-weight: 600; }
.segment-item.active { background: #fff; color: #116b57; box-shadow: 0 1px 3px rgba(22,47,38,.12); }
@media (min-width: 900px) { .page-shell { padding-top: 40rpx; } .panel { padding: 40rpx; } }
</style>
