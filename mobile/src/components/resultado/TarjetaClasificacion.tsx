import { Ionicons } from '@expo/vector-icons';
import { StyleSheet, View } from 'react-native';

import type { ResultadoClasificacion } from '../../servicios/api';
import { espacio, useTema } from '../../theme';
import { Insignia } from '../Insignia';
import { Tarjeta } from '../Tarjeta';
import { Texto } from '../Texto';

const COLOR_BACHE = '#DC2626';
const COLOR_SIN_BACHE = '#16A34A';
const COLOR_AVISO = '#D97706';

/** Resultado del clasificador: veredicto, probabilidad y avisos. */
export function TarjetaClasificacion({ resultado }: { resultado: ResultadoClasificacion }) {
  const { paleta } = useTema();
  const color = resultado.es_bache ? COLOR_BACHE : COLOR_SIN_BACHE;
  const icono = resultado.es_bache ? 'alert-circle' : 'checkmark-circle';
  const titulo = resultado.es_bache ? 'Posible bache' : 'Sin bache visible';
  const porcentaje = Math.round(resultado.probabilidad_bache * 100);
  const umbral = Math.round(resultado.umbral * 100);
  const dudoso = Math.abs(resultado.probabilidad_bache - resultado.umbral) < 0.1;

  return (
    <Tarjeta>
      <View
        style={estilos.contenido}
        accessible
        accessibilityLabel={`${titulo}, probabilidad de bache ${porcentaje} por ciento`}
      >
        <View style={estilos.fila}>
          <View style={[estilos.icono, { backgroundColor: color + '22' }]}>
            <Ionicons name={icono} size={28} color={color} />
          </View>
          <View style={estilos.texto}>
            <Texto variante="subtitulo">{titulo}</Texto>
            <Texto variante="pequeno" suave>
              Probabilidad de bache {porcentaje} %
            </Texto>
          </View>
        </View>

        <View style={[estilos.pista, { backgroundColor: paleta.superficieAlta }]}>
          <View style={[estilos.relleno, { width: `${porcentaje}%`, backgroundColor: color }]} />
        </View>
        <Texto variante="micro" suave>
          El modelo marca bache desde {umbral} %.
        </Texto>

        {dudoso ? (
          <View style={estilos.aviso}>
            <Ionicons name="help-circle" size={18} color={COLOR_AVISO} />
            <Texto variante="pequeno" suave>
              Resultado dudoso: la probabilidad está muy cerca del umbral. Toma otra foto más de cerca y con buena luz.
            </Texto>
          </View>
        ) : null}

        {resultado.advertencia ? (
          <View style={estilos.aviso}>
            <Ionicons name="warning" size={18} color={COLOR_AVISO} />
            <Texto variante="pequeno" suave>
              {resultado.advertencia}
            </Texto>
          </View>
        ) : null}

        <Insignia texto={`Modelo ${resultado.modelo.version}`} icono="hardware-chip-outline" />
      </View>
    </Tarjeta>
  );
}

const estilos = StyleSheet.create({
  contenido: { gap: espacio.md },
  fila: { flexDirection: 'row', alignItems: 'center', gap: espacio.md },
  icono: { width: 56, height: 56, borderRadius: 28, alignItems: 'center', justifyContent: 'center' },
  texto: { flex: 1, gap: 2 },
  pista: { height: 10, borderRadius: 5, overflow: 'hidden' },
  relleno: { height: 10, borderRadius: 5 },
  aviso: { flexDirection: 'row', alignItems: 'flex-start', gap: espacio.sm },
});