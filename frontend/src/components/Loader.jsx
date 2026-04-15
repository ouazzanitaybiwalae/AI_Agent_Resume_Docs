import { useEffect, useState } from 'react'

const STEPS = [
  'Lecture du fichier…',
  'Découpage en chunks…',
  'Résumé local des sections…',
  'Fusion des résumés…',
  'Optimisation finale…',
]

function Loader() {
  const [stepIndex, setStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const TARGETS = [10, 30, 55, 78, 92]

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIndex((i) => {
        const next = Math.min(i + 1, STEPS.length - 1)
        setProgress(TARGETS[next])
        return next
      })
    }, 1600)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="loader">
      <div className="loader-ring" />
      <div className="loader-bar-track">
        <div className="loader-bar-fill" style={{ width: `${progress}%` }} />
      </div>
      <p className="loader-step">{STEPS[stepIndex]}</p>
    </div>
  )
}

export default Loader
