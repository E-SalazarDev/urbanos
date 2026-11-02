const URL_BASE = (process.env.EXPO_PUBLIC_API_URL ?? '').replace(/\/$/, '');
const TIEMPO_MAXIMO_MS = 30000;
const TIEMPO_CONSULTA_MS = 8000;

export type ResultadoClasificacion = {
  simulado: boolean;
  modelo: { nombre: string; version: string };
  imagen: { ancho: number; alto: number };
  es_bache: boolean;
  probabilidad_bache: number;
  umbral: number;
  caracteristicas: Record<string, number>;
  fuera_de_rango: string[];
  advertencia: string | null;
};

export type FichaModelo = {
  nombre: string;
  version: string;
  algoritmo: string;
  umbral: number;
  dataset: string;
  metricas_prueba: Record<string, number> | null;
  columnas_entrada: string[];
};

export type EstadoServicio = {
  disponible: boolean;
  modelo: FichaModelo | null;
};

export class ErrorApi extends Error {}

type RespuestaHttp = { estado: number; texto: string };

/** Envía un formulario con XMLHttpRequest, que entiende los archivos de React Native. */
function enviarFormulario(url: string, formulario: FormData, tiempoMs: number): Promise<RespuestaHttp> {
  return new Promise((resolver, rechazar) => {
    const peticion = new XMLHttpRequest();
    peticion.open('POST', url);
    peticion.setRequestHeader('Accept', 'application/json');
    peticion.timeout = tiempoMs;
    peticion.onload = () => resolver({ estado: peticion.status, texto: peticion.responseText });
    peticion.onerror = () => rechazar(new Error('sin conexión'));
    peticion.ontimeout = () => rechazar(new Error('tiempo agotado'));
    peticion.send(formulario);
  });
}

async function pedirJson<T>(ruta: string): Promise<{ estado: number; datos: T | null }> {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIEMPO_CONSULTA_MS);
  try {
    const respuesta = await fetch(`${URL_BASE}${ruta}`, { signal: control.signal });
    let datos: T | null = null;
    try {
      datos = (await respuesta.json()) as T;
    } catch {
      datos = null;
    }
    return { estado: respuesta.status, datos };
  } finally {
    clearTimeout(temporizador);
  }
}

/** Pregunta al servicio de IA si está disponible y qué modelo tiene cargado. */
export async function consultarServicio(): Promise<EstadoServicio> {
  if (!URL_BASE) {
    throw new ErrorApi('Falta configurar EXPO_PUBLIC_API_URL en el archivo mobile/.env.local.');
  }
  try {
    const [salud, modelo] = await Promise.all([
      pedirJson<{ estado: string }>('/salud'),
      pedirJson<FichaModelo>('/clasificar/modelo'),
    ]);
    return {
      disponible: salud.estado === 200,
      modelo: modelo.estado === 200 ? modelo.datos : null,
    };
  } catch {
    throw new ErrorApi(`No se pudo conectar con el servicio en ${URL_BASE}.`);
  }
}

/** Envía la foto al servicio de IA y devuelve si muestra un bache. */
export async function clasificarFoto(uri: string): Promise<ResultadoClasificacion> {
  if (!URL_BASE) {
    throw new ErrorApi('Falta configurar EXPO_PUBLIC_API_URL en el archivo mobile/.env.local.');
  }

  const formulario = new FormData();
  formulario.append('archivo', { uri, name: 'foto.jpg', type: 'image/jpeg' } as unknown as Blob);

  let respuesta: RespuestaHttp;
  try {
    respuesta = await enviarFormulario(`${URL_BASE}/clasificar`, formulario, TIEMPO_MAXIMO_MS);
  } catch (error) {
    const motivo = error instanceof Error ? error.message : String(error);
    if (motivo === 'tiempo agotado') {
      throw new ErrorApi('El servicio tardó demasiado en responder.');
    }
    throw new ErrorApi(
      `No se pudo conectar con el servicio en ${URL_BASE}. Revisa que el teléfono y la computadora estén en la misma red Wi-Fi.`,
    );
  }

  if (respuesta.estado < 200 || respuesta.estado >= 300) {
    let detalle = '';
    try {
      const cuerpo = JSON.parse(respuesta.texto);
      detalle = typeof cuerpo.detail === 'string' ? cuerpo.detail : '';
    } catch {
      detalle = '';
    }
    throw new ErrorApi(detalle || `El servicio respondió con el código ${respuesta.estado}.`);
  }

  try {
    return JSON.parse(respuesta.texto) as ResultadoClasificacion;
  } catch {
    throw new ErrorApi('El servicio respondió algo que la app no entiende.');
  }
}