import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { StyleSheet, View } from 'react-native';

import { consultarServicio, type EstadoServicio } from '../../servicios/api';
import { espacio } from '../../theme';
import { Boton } from '../Boton';
import { Esqueleto } from '../Esqueleto';
import { Insignia } from '../Insignia';
import { Tarjeta } from '../Tarjeta';
import { Texto } from '../Texto';

const COLOR_OK = '#16A34A';
const COLOR_ERROR = '#DC2626';

type Fase = 'cargando' | 'conectado' | 'sinConexion';

function porcentaje(valor: number | undefined) {
  return valor === undefined ? '—' : `${Math.round(valor * 100)} %`;
}

/** Muestra si el servicio de IA responde y qué modelo tiene cargado. */
export function TarjetaServicioIA() {
  const [fase, setFase] = useState<Fase>('cargando');
  const [estado, setEstado] = useState<EstadoServicio | null>(null);

  const consultar = useCallback(() => {
    let vigente = true;
    setFase('cargando');
    consultarServicio()
      .then((resultado) => {
        if (!vigente) return;
        setEstado(resultado);
        setFase(resultado.disponible ? 'conectado' : 'sinConexion');
      })
      .catch(() => {
        if (!vigente) return;
        setEstado(null);
        setFase('sinConexion');
      });
    return () => {
      vigente = false;
    };
  }, []);

  useFocusEffect(consultar);

  const modelo = estado?.modelo ?? null;
  const metricas = modelo?.metricas_prueba ?? undefined;

  return (
    <Tarjeta>
      <View style={estilos.encabezado}>
        <View style={estilos.titulo}>
          <Ionicons
            name={fase === 'conectado' ? 'cloud-done-outline' : 'cloud-offline-outline'}
            size={22}
            color={fase === 'conectado' ? COLOR_OK : fase === 'sinConexion' ? COLOR_ERROR : '#6B7280'}
          />
          <Texto variante="subtitulo">Servicio de IA</Texto>
        </View>
        {fase === 'conectado' ? (
          <Insignia texto="Conectado" icono="checkmark-circle" color={COLOR_OK} />
        ) : null}
        {fase === 'sinConexion' ? (
          <Insignia texto="Sin conexión" icono="close-circle" color={COLOR_ERROR} />
        ) : null}
      </View>

      {fase === 'cargando' ? (
        <>
          <Esqueleto alto={16} ancho="70%" />
          <Esqueleto alto={14} ancho="50%" />
        </>
      ) : null}

      {fase === 'conectado' && modelo ? (
        <>
          <Texto variante="cuerpoFuerte">
            {modelo.nombre} · {modelo.version}
          </Texto>
          <View style={estilos.fila}>
            <Insignia texto={`Exactitud ${porcentaje(metricas?.accuracy)}`} icono="analytics-outline" />
            <Insignia texto={`Sensibilidad ${porcentaje(metricas?.recall)}`} icono="search-outline" />
            <Insignia texto={`F1 ${metricas?.f1 !== undefined ? metricas.f1.toFixed(2) : '—'}`} icono="ribbon-outline" />
          </View>
          <Texto variante="pequeno" suave>
            Dice si una foto muestra un bache. Todavía no marca dónde está ni cuántos hay.
          </Texto>
        </>
      ) : null}

      {fase === 'conectado' && !modelo ? (
        <Texto variante="pequeno" suave>
          El servicio responde, pero no tiene un modelo cargado.
        </Texto>
      ) : null}

      {fase === 'sinConexion' ? (
        <>
          <Texto variante="pequeno" suave>
            No se pudo contactar el servicio. Revisa que el contenedor esté encendido y que el teléfono esté en la misma red Wi-Fi.
          </Texto>
          <Boton texto="Reintentar" icono="refresh" variante="secundario" onPress={consultar} />
        </>
      ) : null}
    </Tarjeta>
  );
}

const estilos = StyleSheet.create({
  encabezado: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: espacio.sm },
  titulo: { flexDirection: 'row', alignItems: 'center', gap: espacio.sm },
  fila: { flexDirection: 'row', flexWrap: 'wrap', gap: espacio.sm },
});