import { CameraView, useCameraPermissions } from 'expo-camera';
import { useFocusEffect } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useCallback, useRef, useState } from 'react';
import { ActivityIndicator, Image, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Boton } from '../../components/Boton';

import { BotonDisparo } from '@/components/camara/BotonDisparo';
import { BotonIcono } from '@/components/camara/BotonIcono';
import { COLORES_CAMARA } from '@/components/camara/colores';
import { Pantalla } from '../../components/Pantalla';
import { TarjetaClasificacion } from '../../components/resultado/TarjetaClasificacion';
import { Texto } from '../../components/Texto';
import { clasificarFoto, type ResultadoClasificacion } from '../../servicios/api';
import { espacio, radio } from '../../theme';

type Fase = 'visor' | 'analizando' | 'resultado' | 'error';

/** Toma una foto con la cámara y la manda al servicio de IA para saber si muestra un bache. */
export default function Capturar() {
  const insets = useSafeAreaInsets();
  const camara = useRef<CameraView>(null);
  const [permiso, pedirPermiso] = useCameraPermissions();
  const [enFoco, setEnFoco] = useState(false);
  const [frontal, setFrontal] = useState(false);
  const [fase, setFase] = useState<Fase>('visor');
  const [ocupado, setOcupado] = useState(false);
  const [uriFoto, setUriFoto] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoClasificacion | null>(null);
  const [mensajeError, setMensajeError] = useState('');

  useFocusEffect(
    useCallback(() => {
      setEnFoco(true);
      return () => setEnFoco(false);
    }, []),
  );

  const analizar = async (uri: string) => {
    setFase('analizando');
    try {
      setResultado(await clasificarFoto(uri));
      setFase('resultado');
    } catch (error) {
      setMensajeError(error instanceof Error ? error.message : 'Ocurrió un error inesperado.');
      setFase('error');
    }
  };

  const disparar = async () => {
    if (ocupado) return;
    setOcupado(true);
    try {
      const foto = await camara.current?.takePictureAsync({ quality: 0.6 });
      if (!foto) {
        setMensajeError('No se pudo tomar la foto. Intenta de nuevo.');
        setFase('error');
        return;
      }
      setUriFoto(foto.uri);
      await analizar(foto.uri);
    } catch {
      setMensajeError('No se pudo tomar la foto. Intenta de nuevo.');
      setFase('error');
    } finally {
      setOcupado(false);
    }
  };

  const volverALaCamara = () => {
    setResultado(null);
    setUriFoto(null);
    setFase('visor');
  };

  if (!permiso) {
    return <View style={estilos.pantalla} />;
  }

  if (!permiso.granted) {
    return (
      <Pantalla titulo="Cámara" subtitulo="UrbanOS necesita la cámara para fotografiar los daños de la calle">
        <Boton texto="Permitir cámara" icono="camera-outline" onPress={pedirPermiso} />
      </Pantalla>
    );
  }

  if (fase === 'analizando') {
    return (
      <Pantalla titulo="Analizando" subtitulo="Estamos revisando la foto">
        {uriFoto ? <Image source={{ uri: uriFoto }} style={estilos.foto} resizeMode="cover" /> : null}
        <View style={estilos.espera}>
          <ActivityIndicator size="large" />
          <Texto variante="pequeno" suave>
            Esto tarda unos segundos…
          </Texto>
        </View>
      </Pantalla>
    );
  }

  if (fase === 'resultado' && resultado) {
    return (
      <Pantalla titulo="Resultado" subtitulo="Clasificación de la foto completa">
        {uriFoto ? <Image source={{ uri: uriFoto }} style={estilos.foto} resizeMode="cover" /> : null}
        <TarjetaClasificacion resultado={resultado} />
        <Texto variante="micro" suave>
          El modelo dice si la foto muestra un bache. Todavía no marca dónde está ni cuántos hay.
        </Texto>
        <Boton texto="Tomar otra foto" icono="camera-outline" onPress={volverALaCamara} />
      </Pantalla>
    );
  }

  if (fase === 'error') {
    return (
      <Pantalla titulo="No se pudo analizar" subtitulo={mensajeError}>
        {uriFoto ? <Image source={{ uri: uriFoto }} style={estilos.foto} resizeMode="cover" /> : null}
        {uriFoto ? <Boton texto="Reintentar" icono="refresh" onPress={() => analizar(uriFoto)} /> : null}
        <Boton texto="Volver a la cámara" icono="camera-outline" variante="secundario" onPress={volverALaCamara} />
      </Pantalla>
    );
  }

  return (
    <View style={estilos.pantalla}>
      {enFoco ? <StatusBar style="light" /> : null}
      {enFoco ? (
        <CameraView ref={camara} style={estilos.camara} facing={frontal ? 'front' : 'back'} />
      ) : null}

      <View style={[estilos.pista, { top: insets.top + espacio.md }]} pointerEvents="none">
        <View style={estilos.pildora}>
          <Texto variante="pequeno" color={COLORES_CAMARA.blanco}>
            Acércate al bache y encuádralo
          </Texto>
        </View>
      </View>

      <View style={estilos.inferior}>
        <View style={estilos.fila}>
          <View style={estilos.hueco} />
          <BotonDisparo onPress={disparar} />
          <BotonIcono
            icono="camera-reverse-outline"
            etiqueta="Girar cámara"
            onPress={() => setFrontal((valor) => !valor)}
          />
        </View>
      </View>
    </View>
  );
}

const estilos = StyleSheet.create({
  pantalla: { flex: 1, backgroundColor: COLORES_CAMARA.fondo },
  camara: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  pista: { position: 'absolute', left: 0, right: 0, alignItems: 'center' },
  pildora: {
    paddingHorizontal: espacio.md,
    paddingVertical: espacio.sm,
    borderRadius: radio.pildora,
    backgroundColor: COLORES_CAMARA.vidrio,
  },
  inferior: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    paddingBottom: espacio.xl,
  },
  fila: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: espacio.xl,
  },
  hueco: { width: 48, height: 48 },
  foto: { width: '100%', aspectRatio: 4 / 3, borderRadius: radio.lg, backgroundColor: '#2A2F36' },
  espera: { alignItems: 'center', gap: espacio.md, paddingVertical: espacio.lg },
});