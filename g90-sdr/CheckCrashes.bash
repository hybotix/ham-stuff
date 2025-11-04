# Check if anything crashed
dmesg | tail -20

# Check the application log
tail -20 ~/G90-SDR/logs/g90_sdr.log

# Check if GQRX is still running
ps aux | grep gqrx

# Check if FlRig is still running
ps aux | grep flrig

# Check audio status
systemctl --user status pulseaudio
