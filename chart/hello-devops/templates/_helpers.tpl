{{/*
Named templates (helpers) that the other templates reuse with "include".
Files that start with an underscore render no objects of their own.
*/}}

{{/* Labels that pick this release's Pods. Never change them after the first install. */}}
{{- define "hello-devops.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* All labels: the selector labels plus information about the chart. */}}
{{- define "hello-devops.labels" -}}
{{ include "hello-devops.selectorLabels" . }}
app.kubernetes.io/version: {{ .Values.image.tag | default .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}
