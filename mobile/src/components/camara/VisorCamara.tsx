import { Ionicons } from '@expo/vector-icons';
import type { ReactNode } from 'react';
import { StyleSheet, View, type ViewStyle } from 'react-native';

import { espacio, radio } from '../../theme';
import { Texto } from '../Texto';
import { COLORES_CAMARA } from './colores';

function Esquina({ estilo }: { estilo: ViewStyle }) {
  return <View style={[estilos.esquina, estilo]} />;
}


export function VisorCamara({ children }: { children?: ReactNode }) {
  return (
    <View style={estilos.contenedor}>
      <View style={estilos.centrado} pointerEvents="none">
        <Ionicons name="camera-outline" size={56} color={COLORES_CAMARA.textoSuave} />
        <Texto variante="pequeno" color={COLORES_CAMARA.textoSuave}>
          Vista de la cámara
        </Texto>
      </View>

      <View style={[estilos.lineaVertical, { left: '33.33%' }]} pointerEvents="none" />
      <View style={[estilos.lineaVertical, { left: '66.66%' }]} pointerEvents="none" />
      <View style={[estilos.lineaHorizontal, { top: '33.33%' }]} pointerEvents="none" />
      <View style={[estilos.lineaHorizontal, { top: '66.66%' }]} pointerEvents="none" />

      <View style={estilos.marco} pointerEvents="none">
        <Esquina estilo={{ top: 0, left: 0, borderTopWidth: 4, borderLeftWidth: 4, borderTopLeftRadius: 10 }} />
        <Esquina estilo={{ top: 0, right: 0, borderTopWidth: 4, borderRightWidth: 4, borderTopRightRadius: 10 }} />
        <Esquina estilo={{ bottom: 0, left: 0, borderBottomWidth: 4, borderLeftWidth: 4, borderBottomLeftRadius: 10 }} />
        <Esquina estilo={{ bottom: 0, right: 0, borderBottomWidth: 4, borderRightWidth: 4, borderBottomRightRadius: 10 }} />
      </View>

      <View style={estilos.pista} pointerEvents="none">
        <View style={estilos.pildora}>
          <Texto variante="pequeno" color={COLORES_CAMARA.blanco}>
            Encuadra el daño dentro del marco
          </Texto>
        </View>
      </View>

      {children}
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { flex: 1, backgroundColor: COLORES_CAMARA.fondo, overflow: 'hidden' },
  centrado: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center', gap: espacio.sm },
  lineaVertical: { position: 'absolute', top: 0, bottom: 0, width: 1, backgroundColor: COLORES_CAMARA.linea },
  lineaHorizontal: { position: 'absolute', left: 0, right: 0, height: 1, backgroundColor: COLORES_CAMARA.linea },
  marco: { position: 'absolute', left: '10%', right: '10%', top: '20%', bottom: '32%' },
  esquina: { position: 'absolute', width: 34, height: 34, borderColor: COLORES_CAMARA.blanco },
  pista: { position: 'absolute', left: 0, right: 0, bottom: '24%', alignItems: 'center' },
  pildora: {
    paddingHorizontal: espacio.md,
    paddingVertical: espacio.sm,
    borderRadius: radio.pildora,
    backgroundColor: COLORES_CAMARA.vidrio,
  },
});