FROM python:3-alpine as build

WORKDIR /build
RUN \
    apk update && \
    apk add gcc musl-dev libffi-dev && \
    pip wheel --wheel-dir=/build pyyaml cryptography redis hiredis flask filetype

FROM python:3-alpine

COPY --from=build /build /build
RUN \
    pip install --no-index --find-links=/build pyyaml cryptography redis hiredis flask filetype && \
    rm -rf /build

COPY . /nurdpaste

USER nobody
WORKDIR /nurdpaste
ENTRYPOINT [ "/nurdpaste/nurdpaste.py" ]
