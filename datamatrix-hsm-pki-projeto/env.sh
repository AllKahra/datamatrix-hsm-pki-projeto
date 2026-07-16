#!/usr/bin/env bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$PROJECT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/.env"
  set +a
fi

export PROJECT_DIR
export OUTPUT_DIR="$PROJECT_DIR/output"
export SOFTHSM2_CONF="$OUTPUT_DIR/softhsm2.conf"
export HSM_MODULE="${HSM_MODULE:-/usr/lib/x86_64-linux-gnu/softhsm/libsofthsm2.so}"

export HSM_USER_PIN="${HSM_USER_PIN:-1234}"
export HSM_SO_PIN="${HSM_SO_PIN:-5678}"

export CA_TOKEN_LABEL="${CA_TOKEN_LABEL:-CA-TOKEN}"
export CA_KEY_LABEL="${CA_KEY_LABEL:-CAkey}"
export MANUFACTURER_TOKEN_LABEL="${MANUFACTURER_TOKEN_LABEL:-MFG-TOKEN}"
export MANUFACTURER_KEY_LABEL="${MANUFACTURER_KEY_LABEL:-MFGkey}"

export HSM_CA_KEY="pkcs11:token=${CA_TOKEN_LABEL};object=${CA_KEY_LABEL};type=private"
export HSM_MFG_KEY="pkcs11:token=${MANUFACTURER_TOKEN_LABEL};object=${MANUFACTURER_KEY_LABEL};type=private"

export CA_CRT="$OUTPUT_DIR/pki/ca.crt"
export MFG_CRT="$OUTPUT_DIR/pki/manufacturer.crt"
