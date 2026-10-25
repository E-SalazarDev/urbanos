import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import type { DeteccionEjemplo } from '../../datos/ejemplos';
import { espacio, radio } from '../../theme';
import { CajaDeteccion } from '../detecciones/CajaDeteccion';
import { Texto } from '../Texto';
import { COLORES_CAMARA } from './colores';


export function FotoCapturada({ detecciones }: { detecciones: DeteccionEjemplo[] }) {
  return (
    <View style={estilos.marco} accessible accessibilityLabel="Foto capturada con las detecciones marcadas">
      <View style={estilos.centrado}>
        <Ionicons name="image-outline" size={48} color={COLORES_CAMARA.textoSuave} />
        <Texto variante="pequeno" color={COLORES_CAMARA.textoSuave}>
          Foto de ejemplo
        </Texto>
      </View>
      {detecciones.map((d) => (
        <CajaDeteccion key={d.id} tipo={d.tipo} confianza={d.confianza} caja={d.caja} />
      ))}
    </View>
  );
}

const estilos = StyleSheet.create({
  marco: {
    width: '100%',
    aspectRatio: 4 / 3,
    borderRadius: radio.lg,
    overflow: 'hidden',
    backgroundColor: '#2A2F36',
  },
  centrado: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, alignItems: 'center', justifyContent: 'center', gap: espacio.sm },
});