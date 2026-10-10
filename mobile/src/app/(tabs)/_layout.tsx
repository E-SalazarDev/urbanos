import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { Tabs } from 'expo-router';
import { StyleSheet, View, type GestureResponderEvent } from 'react-native';

import { Presionable } from '../../components/Presionable';
import type { NombreIcono } from '../../constants/danos';
import { sombra, useTema } from '../../theme';

type PropsBotonCentral = { onPress?: (e: GestureResponderEvent) => void };


function BotonCentral({ onPress }: PropsBotonCentral) {
  const { paleta } = useTema();
  return (
    <View style={estilos.centroContenedor}>
      <Presionable
        onPress={onPress}
        accessibilityLabel="Capturar foto"
        estilo={[estilos.centro, { backgroundColor: paleta.primario }, sombra(2)]}
      >
        <Ionicons name="camera" size={26} color={paleta.sobrePrimario} />
      </Presionable>
    </View>
  );
}

function icono(activo: NombreIcono, inactivo: NombreIcono) {
  const Icono = ({ color, focused }: { color: string; focused: boolean }) => (
    <Ionicons name={focused ? activo : inactivo} size={24} color={color} />
  );
  return Icono;
}

export default function TabsLayout() {
  const { paleta } = useTema();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: paleta.primario,
        tabBarInactiveTintColor: paleta.textoSuave,
        tabBarStyle: {
          backgroundColor: paleta.superficie,
          borderTopColor: paleta.borde,
          borderTopWidth: StyleSheet.hairlineWidth,
          paddingTop: 6,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
      }}
    
      screenListeners={{ tabPress: () => void Haptics.selectionAsync() }}
    >
      <Tabs.Screen name="index" options={{ title: 'Inicio', tabBarIcon: icono('home', 'home-outline') }} />
      <Tabs.Screen name="mapa" options={{ title: 'Mapa', tabBarIcon: icono('map', 'map-outline') }} />
      <Tabs.Screen
        name="capturar"
        options={{ title: 'Capturar', tabBarButton: (props) => <BotonCentral onPress={props.onPress} /> }}
      />
      <Tabs.Screen
        name="reportes"
        options={{ title: 'Reportes', tabBarIcon: icono('document-text', 'document-text-outline') }}
      />
      <Tabs.Screen name="perfil" options={{ title: 'Perfil', tabBarIcon: icono('person', 'person-outline') }} />
    </Tabs>
  );
}

const estilos = StyleSheet.create({
  centroContenedor: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  centro: { width: 52, height: 52, borderRadius: 26, alignItems: 'center', justifyContent: 'center' },
});
