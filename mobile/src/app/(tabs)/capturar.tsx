import { useFocusEffect } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useCallback, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Boton } from '../../components/Boton';
import { BotonDisparo } from '../../components/camara/BotonDisparo';
import { BotonIcono } from '../../components/camara/BotonIcono';
import { COLORES_CAMARA } from '../../components/camara/colores';
import { EstadoGps } from '../../components/camara/EstadoGps';
import { FotoCapturada } from '../../components/camara/FotoCapturada';
import { SelectorModo, type ModoCaptura } from '../../components/camara/SelectorModo';
import { VisorCamara } from '../../components/camara/VisorCamara';
import { TarjetaDeteccion } from '../../components/detecciones/TarjetaDeteccion';
import { Insignia } from '../../components/Insignia';
import { Pantalla } from '../../components/Pantalla';
import { Texto } from '../../components/Texto';
import { DETECCIONES_EJEMPLO } from '../../datos/ejemplos';
import { espacio } from '../../theme';


export default function Capturar() {
  const insets = useSafeAreaInsets();
  const [modo, setModo] = useState<ModoCaptura>('foto');
  const [fase, setFase] = useState<'visor' | 'resultado'>('visor');
  const [enFoco, setEnFoco] = useState(false);

  useFocusEffect(
    useCallback(() => {
      setEnFoco(true);
      return () => setEnFoco(false);
    }, []),
  );

  if (fase === 'resultado') {
    return (
      <Pantalla titulo="Detecciones" subtitulo="Revisa el resultado antes de enviar">
        <FotoCapturada detecciones={DETECCIONES_EJEMPLO} />

        <View style={estilos.encabezadoLista}>
          <Texto variante="subtitulo">{DETECCIONES_EJEMPLO.length} daños encontrados</Texto>
          <Insignia texto="Datos de ejemplo" icono="flask-outline" />
        </View>

        {DETECCIONES_EJEMPLO.map((d) => (
          <TarjetaDeteccion key={d.id} tipo={d.tipo} confianza={d.confianza} />
        ))}

        <Boton texto="Enviar" icono="cloud-upload-outline" />
        <Boton texto="Repetir" icono="refresh" variante="secundario" onPress={() => setFase('visor')} />
      </Pantalla>
    );
  }

  return (
    <View style={estilos.pantalla}>
      {enFoco ? <StatusBar style="light" /> : null}
      <VisorCamara>
        <View style={[estilos.superior, { paddingTop: insets.top + espacio.sm }]}>
          <EstadoGps estado="listo" />
          <BotonIcono icono="flash-off" etiqueta="Flash apagado" />
        </View>

        <View style={estilos.inferior}>
          <SelectorModo modo={modo} onCambiar={setModo} />
          <View style={estilos.fila}>
            <BotonIcono icono="images-outline" etiqueta="Abrir galería" />
            <BotonDisparo modo={modo} onPress={() => setFase('resultado')} />
            <BotonIcono icono="camera-reverse-outline" etiqueta="Girar cámara" />
          </View>
        </View>
      </VisorCamara>
    </View>
  );
}

const estilos = StyleSheet.create({
  pantalla: { flex: 1, backgroundColor: COLORES_CAMARA.fondo },
  superior: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: espacio.md,
  },
  inferior: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    gap: espacio.md,
    paddingBottom: espacio.lg,
  },
  fila: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: espacio.xl,
  },
  encabezadoLista: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: espacio.sm,
  },
});