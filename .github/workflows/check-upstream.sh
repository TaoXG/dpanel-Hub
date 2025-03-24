     #!/bin/bash
     UPSTREAM_IMAGE="dpanel/dpanel:lite"
     LATEST_DIGEST=$(docker pull $UPSTREAM_IMAGE --quiet | awk '{print $1}')
     CURRENT_DIGEST=$(docker images --digests --format "{{.Digest}}" $UPSTREAM_IMAGE)

     if [ "$LATEST_DIGEST" != "$CURRENT_DIGEST" ]; then
       echo "New version detected!"
       exit 1
     else
       echo "No updates."
       exit 0
     fi
