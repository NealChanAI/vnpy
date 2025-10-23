@echo off
chcp 65001 >nul
cls
echo ============================================================
echo VeighNa 期货全量数据下载（健壮版）
echo ============================================================
echo.
echo 改进功能：
echo   ✓ 处理NULL值
echo   ✓ API限制自动重试
echo   ✓ 断点续传
echo   ✓ 完善错误处理
echo.
echo 品种数量：42个
echo 预计耗时：3-4小时
echo 日志文件：download_progress.log
echo 进度文件：download_state.json
echo.
echo ============================================================
echo.
echo 激活vnpy环境...
call conda activate vnpy
echo.
echo 开始下载...
echo.
cd /d "%~dp0\.."
python src\data_process\download_robust.py
echo.
echo ============================================================
echo 下载结束
echo ============================================================
pause

