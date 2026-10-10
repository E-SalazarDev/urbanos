import { useEffect, useRef } from 'react';
import { Animated, type DimensionValue } from 'react-native';

import { radio, useTema } from '../theme';

type Props = {
  ancho?: DimensionValue;
  alto?: number;
  radioBorde?: number;
};


export function Esqueleto({ ancho = '100%', alto = 16, radioBorde = radio.sm }: Props) {
  const { paleta } = useTema();
  const opacidad = useRef(new Animated.Value(0.5)).current;

  useEffect(() => {
    const animacion = Animated.loop(
      Animated.sequence([
        Animated.timing(opacidad, { toValue: 1, duration: 800, useNativeDriver: true }),
        Animated.timing(opacidad, { toValue: 0.5, duration: 800, useNativeDriver: true }),
      ]),
    );
    animacion.start();
    return () => animacion.stop();
  }, [opacidad]);

  return (
    <Animated.View
      accessibilityElementsHidden
      importantForAccessibility="no-hide-descendants"
      style={{ width: ancho, height: alto, borderRadius: radioBorde, backgroundColor: paleta.superficieAlta, opacity: opacidad }}
    />
  );
}
