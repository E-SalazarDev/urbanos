import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import { TIPOS_DANO, type TipoDano } from '../../constants/danos';
import { espacio, useTema } from '../../theme';
import { Insignia } from '../Insignia';
import { Tarjeta } from '../Tarjeta';
import { Texto } from '../Texto';

type Props = {
  tipo: TipoDano;
  confianza: number;
};

export function TarjetaDeteccion({ tipo, confianza }: Props) {
  const { paleta } = useTema();
  const info = TIPOS_DANO[tipo];
  const porcentaje = Math.round(confianza * 100);

  return (
    <Tarjeta>
      <View
        style={estilos.fila}
        accessible
        accessibilityLabel={`${info.nombre}, confianza ${porcentaje} por ciento`}
      >
        <View style={[estilos.icono, { backgroundColor: info.color + '22' }]}>
          <Ionicons name={info.icono} size={24} color={info.color} />
        </View>

        <View style={estilos.contenido}>
          <View style={estilos.encabezado}>
            <Texto variante="cuerpoFuerte">{info.nombre}</Texto>
            <Insignia texto={tipo} />
          </View>
          <View style={[estilos.pista, { backgroundColor: paleta.superficieAlta }]}>
            <View style={[estilos.relleno, { width: `${porcentaje}%`, backgroundColor: info.color }]} />
          </View>
          <Texto variante="pequeno" suave>
            Confianza {porcentaje} %
          </Texto>
        </View>
      </View>
    </Tarjeta>
  );
}

const estilos = StyleSheet.create({
  fila: { flexDirection: 'row', alignItems: 'center', gap: espacio.md },
  icono: { width: 48, height: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  contenido: { flex: 1, gap: espacio.sm },
  encabezado: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: espacio.sm },
  pista: { height: 8, borderRadius: 4, overflow: 'hidden' },
  relleno: { height: 8, borderRadius: 4 },
});