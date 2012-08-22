kill $(ps | grep 'python' | awk '{print $1}')
kill $(ps | grep 'twistd' | awk '{print $1}')
