import { useRouter } from 'expo-router';
import { StyleSheet, View } from 'react-native';

import { Boton } from '../../components/Boton';
import { Esqueleto } from '../../components/Esqueleto';
import { Insignia } from '../../components/Insignia';
import { Pantalla } from '../../components/Pantalla';
import { Tarjeta } from '../../components/Tarjeta';
import { Texto } from '../../components/Texto';
import { TIPOS_DANO } from '../../constants/danos';
import { espacio } from '../../theme';

export default function Inicio() {
  const router = useRouter();

  return (
    <Pantalla titulo="UrbanOS" subtitulo="Cuida las calles de tu ciudad">
      <Tarjeta>
        <Texto variante="subtitulo">Resumen</Texto>
       
        <Esqueleto alto={20} ancho="60%" />
        <Esqueleto alto={14} ancho="90%" />
        <Texto variante="pequeno" suave>
          Aún no hay datos. Aparecerán cuando la app se conecte con el servidor.
        </Texto>
      </Tarjeta>

      <Boton texto="Capturar foto" icono="camera" onPress={() => router.push('/capturar')} />

      <Tarjeta>
        <Texto variante="subtitulo">Tipos de daño</Texto>
        <View style={estilos.fila}>
          {Object.entries(TIPOS_DANO).map(([codigo, d]) => (
            <Insignia key={codigo} texto={d.nombre} icono={d.icono} color={d.color} />
          ))}
        </View>
      </Tarjeta>

      <Tarjeta>
        <Texto variante="subtitulo">Próximamente</Texto>
        <View style={estilos.fila}>
          <Insignia texto="Reportes ciudadanos" icono="time-outline" />
          <Insignia texto="Órdenes de trabajo" icono="time-outline" />
        </View>
      </Tarjeta>
    </Pantalla>
  );
}

const estilos = StyleSheet.create({
  fila: { flexDirection: 'row', flexWrap: 'wrap', gap: espacio.sm },
});
