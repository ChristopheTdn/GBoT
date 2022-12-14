#!/bin/sh -e
#
### BEGIN INIT INFO
# Provides:          gbot
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: description du programme
### END INIT INFO
DAEMON="/root/miniconda3/envs/gbot/bin/python" #ligne de commande du programme, attention Ã  l'extension .py.
daemon_OPT="/root/GBoT/gbot.py"  #argument Ã  utiliser par le programme - Remplacer Utilisateur par votre nom de login
DAEMONUSER="root" #utilisateur du programme
daemon_NAME="gbot.py" #Nom du programme (doit Ãªtre identique Ã  l'exÃ©cutable).
#Attention le script est un script bash, le script ne portera donc pas l'extension .py mais .sh.

 
PATH="/sbin:/bin:/usr/sbin:/usr/bin" #Ne pas toucher
 
test -x $DAEMON || exit 0
 
. /lib/lsb/init-functions

d_start () {
        log_daemon_msg "Starting system $daemon_NAME Daemon"
	start-stop-daemon --background --name $daemon_NAME --start --quiet --chuid $DAEMONUSER --exec $DAEMON -- $daemon_OPT
        log_end_msg $?
}
 
d_stop () {
        log_daemon_msg "Stopping system $daemon_NAME Daemon"
        start-stop-daemon --name $daemon_NAME --stop --retry 5 --quiet --name $daemon_NAME
	log_end_msg $?
}
 
case "$1" in
 
        start|stop)
                d_${1}
                ;;
 
        restart|reload|force-reload)
                        d_stop
                        d_start
                ;;
 
        force-stop)
               d_stop
                killall -q $daemon_NAME || true
                sleep 2
                killall -q -9 $daemon_NAME || true
                ;;
 
        status)
                status_of_proc "$daemon_NAME" "$DAEMON" "system-wide $daemon_NAME" && exit 0 || exit $?
                ;;
        *)
                echo "Usage: /etc/init.d/$daemon_NAME {start|stop|force-stop|restart|reload|force-reload|status}"
                exit 1
                ;;
esac
exit 0