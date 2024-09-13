#!/bin/bash

TMPDIR="/tmp/esgf/$2"
mkdir -p $TMPDIR
MAPFILE="$TMPDIR/mapfile.json"
SCANFILE="$TMPDIR/scanfile.json"
PUBRECFILE="$TMPDIR/pubrec.json"
PIDFILE="$TMPDIR/pid.json"
DATAROOT="/eagle/projects/ESGF2/esg_dataroot/css03_data"

python3.11 ~/repos/esg-publisher/scripts/generate_mapfile.py ${DATAROOT} $1 $MAPFILE
rc=$?
if [ $rc -ne 0 ]; then
    exit $rc
fi

~/miniconda3/envs/esgf-pub/bin/autocurator --out_pretty --files "${DATAROOT}/$1/*.nc" --out_json $SCANFILE
rc=$?
if [ $rc -ne 0 ]; then
    exit $rc
fi

~/miniconda3/envs/esgf-pub/bin/esgmkpubrec --map-data $MAPFILE --scan-file $SCANFILE --out-file $PUBRECFILE
rc=$?
if [ $rc -ne 0 ]; then
    exit $rc
fi

~/miniconda3/envs/esgf-pub/bin/esgpidcitepub --pub-rec $PUBRECFILE --out-file $PIDFILE
rc=$?
if [ $rc -ne 0 ]; then
    exit $rc
fi

~/miniconda3/envs/esgf-pub/bin/esgindexpub --pub-rec $PIDFILE --no-auth
rc=$?
if [ $rc -ne 0 ]; then
    exit $rc
fi

exit 0
