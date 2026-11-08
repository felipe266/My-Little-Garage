#version 460

in vec2 textureCoord;
in vec3 worldPos;

out vec4 fragColor;

uniform sampler2D imagem;
uniform bool usarLuz;
uniform bool isSombra;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform vec3 camPos;
uniform vec3 camDir;

float calcularIluminacao(vec3 A, vec3 B) {
    return A.x * B.x +
           A.y * B.y +
           A.z * B.z;
}

vec3 calcularNormal(vec3 A, vec3 B) {
    return vec3(
        A.y * B.z - A.z * B.y,
        A.z * B.x - A.x * B.z,
        A.x * B.y - A.y * B.x
    );
}

void main(){
    vec4 cor = texture(imagem, textureCoord);
    if (cor.a < 0.01){
        discard;
    }

    if (isSombra) {
        fragColor = vec4(0.06, 0.06, 0.10, 0.45);
        return;
    }

    if (!usarLuz) {
        fragColor = cor;
        return;
    }

    vec3 N = normalize(calcularNormal(dFdx(worldPos), dFdy(worldPos)));

    vec3 V = normalize(camPos - worldPos);
    if (calcularIluminacao(N, V) < 0.0) {
        N = -N;
    }

    vec3 L = normalize(camPos - worldPos);
    vec3 dirPixel = -L;

    float anguloCone = calcularIluminacao(dirPixel, camDir);
    float intensidadeLanterna = 0.0;
    if (anguloCone > 0.91) {
        intensidadeLanterna = (anguloCone - 0.91) / (1.0 - 0.91);
        intensidadeLanterna = intensidadeLanterna * intensidadeLanterna;
    }

    float dist = length(camPos - worldPos);
    float atenuacao = 1.0 / (1.0 + 0.015 * dist);

    float diff = max(calcularIluminacao(N, L), 0.0) * intensidadeLanterna * atenuacao;

    vec3 iluminacao = ambientColor + lightColor * diff;

    fragColor = vec4(cor.rgb * iluminacao, cor.a);
}