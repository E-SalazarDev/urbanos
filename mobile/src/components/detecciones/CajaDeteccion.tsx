import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import { TIPOS_DANO, type TipoDano } from '../../constants/danos';
import { espacio } from '../../theme';
import { Texto } from '../Texto';

type Props = {
  tipo: TipoDano;
  confianza: number;
  caja: { x: number; y: number; ancho: number; alto: number };
};


export function CajaDeteccion({ tipo, confianza, caja }: Props) {
  const info = TIPOS_DANO[tipo];

  return (
    <View
      pointerEvents="none"
      style={[
        estilos.caja,
        {
          left: `${caja.x}%`,
          top: `${caja.y}%`,
          width: `${caja.ancho}%`,
          height: `${caja.alto}%`,
          borderColor: info.color,
        },
      ]}
    >
      <View style={estilos.etiqueta}>
        <Ionicons name={info.icono} size={12} color={info.color} />
        <Texto variante="micro" color="#FFFFFF">
          {info.nombre} {Math.round(confianza * 100)} %
        </Texto>
      </View>
    </View>
  );
}

const estilos = StyleSheet.create({
  caja: { position: 'absolute', borderWidth: 2, borderRadius: 4 },
  etiqueta: {
    position: 'absolute',
    top: 0,
    left: 0,
    flexDirection: 'row',
    alignItems: 'center',
    gap: espacio.xs,
    paddingHorizontal: espacio.sm - 2,
    paddingVertical: 3,
    borderBottomRightRadius: 6,
    backgroundColor: 'rgba(0, 0, 0, 0.65)',
  },
});